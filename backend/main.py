from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import json
import base64
import io
from typing import Optional
import asyncio
import logging
import traceback

from agent import KisanAgent
from tools.rag import RAGTool
from tools.asr import ASRHandler
from tools.tts import TTSHandler
from tools.vision import VisionHandler
from tools.market import MarketDataHandler
from tools.policies import GovernmentPoliciesHandler
from utils import Utils
from config import settings
from memory import ConversationMemory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Kisan Backend",
    description="AI-powered agricultural assistant backend",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Use the property from settings
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None

class MarketRequest(BaseModel):
    crop: str
    location: Optional[str] = None

class PolicyRequest(BaseModel):
    query: str

# Initialize handlers
kisan_agent = KisanAgent()
rag_tool = RAGTool()
asr_handler = ASRHandler()
tts_handler = TTSHandler()
vision_handler = VisionHandler()
market_handler = MarketDataHandler()
policies_handler = GovernmentPoliciesHandler()
memory_store = ConversationMemory(max_messages=40)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if app.debug else None
        }
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "success": True,
        "data": {
            "message": "Project Kisan Backend is running",
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": asyncio.get_event_loop().time()
        }
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "services": {
                "rag": "available",
                "asr": "available", 
                "tts": "available",
                "vision": "available",
                "market": "available",
                "policies": "available"
            },
            "timestamp": asyncio.get_event_loop().time()
        }
    }

@app.post("/api/chat/text")
async def chat_text(request: ChatRequest):
    """Handle text-based queries from farmers"""
    try:
        logger.info(f"Received text query: {request.query}")
        
        # Prepare conversational context
        session_id = request.session_id or "default"
        history = memory_store.get_history(session_id)
        history_context = ConversationMemory.format_history_for_context(history)

        # Process through agent orchestrator with context preface
        enriched_query = (
            f"Conversation so far:\n{history_context}\n\nUser question: {request.query}" if history_context else request.query
        )
        response = await kisan_agent.process_text_query(enriched_query)

        # Save exchange
        memory_store.add_exchange(session_id, request.query, response)
        
        return {
            "success": True,
            "data": {
                "response": response,
                "query": request.query,
                "timestamp": asyncio.get_event_loop().time()
            },
            "message": "Query processed successfully"
        }
    except Exception as e:
        logger.error(f"Error processing text query: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to process query"
            }
        )

@app.post("/api/chat/voice")
async def chat_voice(audio_file: UploadFile = File(...), session_id: str | None = None):
    """Handle voice-based queries from farmers"""
    try:
        logger.info(f"Received voice query from: {audio_file.filename}")
        
        # Read audio file
        audio_content = await audio_file.read()

        # Basic validation before ASR
        validation = Utils.validate_audio_file(audio_content)
        if not validation.get("valid"):
            logger.error(f"Audio validation failed: {validation.get('error')}")
            raise HTTPException(status_code=400, detail=validation.get("error", "Invalid audio file"))
        
        # Convert speech to text
        transcribed_text = await asr_handler.speech_to_text(audio_content)
        
        if not transcribed_text:
            raise HTTPException(status_code=400, detail="Could not transcribe audio")
        
        # Process through agent orchestrator with history context
        sid = session_id or "default"
        history = memory_store.get_history(sid)
        history_context = ConversationMemory.format_history_for_context(history)
        enriched_query = (
            f"Conversation so far:\n{history_context}\n\nUser question: {transcribed_text}" if history_context else transcribed_text
        )
        agent_response = await kisan_agent.process_text_query(enriched_query)
        memory_store.add_exchange(sid, transcribed_text, agent_response)
        
        # Convert response to speech (gracefully handle TTS failures)
        audio_response = await tts_handler.text_to_speech(
            agent_response,
            language_code=settings.TTS_LANGUAGE,
            voice_gender=settings.TTS_VOICE_GENDER,
        )

        audio_b64 = None
        if audio_response:
            audio_b64 = base64.b64encode(audio_response).decode('utf-8')
        else:
            logger.warning("TTS synthesis failed; returning text response without audio")

        return {
            "success": True,
            "data": {
                "transcribed_text": transcribed_text,
                "response_text": agent_response,
                "audio_response": audio_b64,
                "timestamp": asyncio.get_event_loop().time()
            },
            "message": "Voice query processed successfully"
        }
    except HTTPException as e:
        # Allow explicit HTTP errors (e.g., 400) to pass through
        raise e
    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/image")
async def chat_image(
    image_file: UploadFile = File(...),
    query: Optional[str] = None
):
    """Handle image-based queries for crop disease diagnosis"""
    try:
        logger.info(f"Received image query: {image_file.filename}")
        
        # Read image file
        image_content = await image_file.read()
        
        # Analyze image for crop diseases
        diagnosis_result = await vision_handler.analyze_crop_image(image_content)
        
        # If additional query provided, process it with context
        if query:
            full_query = f"Image shows: {diagnosis_result}. Additional question: {query}"
            agent_response = await kisan_agent.process_text_query(full_query)
        else:
            agent_response = await kisan_agent.process_text_query(
                f"Please provide detailed information about this crop condition: {diagnosis_result}"
            )
        
        return {
            "success": True,
            "data": {
                "image_analysis": diagnosis_result,
                "response": agent_response,
                "query": query,
                "timestamp": asyncio.get_event_loop().time()
            },
            "message": "Image analysis completed successfully"
        }
    except Exception as e:
        logger.error(f"Error processing image query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market/prices")
async def get_market_prices(request: MarketRequest):
    """Get real-time market prices for crops"""
    try:
        logger.info(f"Fetching market prices for: {request.crop} in {request.location}")
        
        prices = await market_handler.get_crop_prices(request.crop, request.location)
        
        return {
            "success": True,
            "data": {
                "crop": request.crop,
                "location": request.location,
                "prices": prices,
                "timestamp": asyncio.get_event_loop().time()
            },
            "message": "Market prices fetched successfully"
        }
    except Exception as e:
        logger.error(f"Error fetching market prices: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to fetch market prices"
            }
        )

@app.post("/api/policies/search")
async def search_policies(request: PolicyRequest):
    """Search government agricultural policies and schemes"""
    try:
        logger.info(f"Searching policies for: {request.query}")
        
        policies = await policies_handler.search_policies(request.query)
        
        return {
            "success": True,
            "data": {
                "query": request.query,
                "policies": policies,
                "timestamp": asyncio.get_event_loop().time()
            },
            "message": "Policies search completed successfully"
        }
    except Exception as e:
        logger.error(f"Error searching policies: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to search policies"
            }
        )

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            content = message.get("content")
            
            if message_type == "text":
                # Process text query
                response = await kisan_agent.process_text_query(content)
                await websocket.send_text(json.dumps({
                    "type": "text_response",
                    "content": response
                }))
            
            elif message_type == "voice":
                # Process voice query
                audio_data = base64.b64decode(content)
                transcribed_text = await asr_handler.speech_to_text(audio_data)
                agent_response = await kisan_agent.process_text_query(transcribed_text)
                audio_response = await tts_handler.text_to_speech(agent_response)
                
                await websocket.send_text(json.dumps({
                    "type": "voice_response",
                    "transcribed_text": transcribed_text,
                    "response_text": agent_response,
                    "audio_response": base64.b64encode(audio_response).decode('utf-8')
                }))
            
            elif message_type == "image":
                # Process image query
                image_data = base64.b64decode(content)
                query_text = message.get("query", "")
                
                diagnosis_result = await vision_handler.analyze_crop_image(image_data)
                
                if query_text:
                    full_query = f"Image shows: {diagnosis_result}. Additional question: {query_text}"
                    agent_response = await kisan_agent.process_text_query(full_query)
                else:
                    agent_response = await kisan_agent.process_text_query(
                        f"Please provide detailed information about this crop condition: {diagnosis_result}"
                    )
                
                await websocket.send_text(json.dumps({
                    "type": "image_response",
                    "image_analysis": diagnosis_result,
                    "response": agent_response
                }))
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": str(e)
        }))

@app.get("/api/health")
async def health_check():
    """Comprehensive health check for all services"""
    health_status = {
        "status": "healthy",
        "services": {
            "agent": "healthy",
            "rag": "healthy",
            "asr": "healthy",
            "tts": "healthy",
            "vision": "healthy",
            "market": "healthy",
            "policies": "healthy"
        }
    }
    
    # Check each service
    try:
        # Test RAG connection
        await rag_tool.test_connection()
    except Exception as e:
        health_status["services"]["rag"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 