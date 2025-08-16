# backend/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import Optional, Dict, Any, List
import base64
import logging
from loguru import logger

# Import schemas
from schemas.schemas import (
    DiagnoseRequest,
    MarketQuery,
    WeatherQuery,
    SchemesQuery,
    AgentResponse
)

# Import orchestrator
from ..orchestartor import orchestrator, AgentType

# Create router
router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "kisan-ai-backend"}

@router.post("/diagnose", response_model=Dict[str, Any])
async def diagnose_plant(
    image: UploadFile = File(...),
    crop: str = Form(...),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None)
):
    """
    Diagnose plant disease from an image
    
    Args:
        image: Image file of the plant
        crop: Type of crop
        lat: Optional latitude for weather data
        lon: Optional longitude for weather data
    """
    try:
        # Read image data
        image_data = await image.read()
        
        # Create request object
        diagnose_req = DiagnoseRequest(
            image_b64=base64.b64encode(image_data).decode('utf-8'),
            crop=crop
        )
        
        # Call orchestrator
        response = await orchestrator.run_full_pipeline(
            diagnose_req=diagnose_req,
            lat=lat,
            lon=lon
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in diagnose_plant: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market", response_model=Dict[str, Any])
async def get_market_insights(
    commodity: str, 
    state: Optional[str] = None, 
    district: Optional[str] = None
):
    """
    Get market insights and price information
    """
    try:
        market_query = MarketQuery(
            commodity=commodity,
            state=state,
            district=district
        )
        
        response = await orchestrator.process_request(
            AgentType.MARKET,
            market_query.dict()
        )
        return response
    except Exception as e:
        logger.error(f"Error in get_market_insights: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather", response_model=Dict[str, Any])
async def get_weather(
    lat: float,
    lon: float
):
    """
    Get weather information for a location
    """
    try:
        weather_query = WeatherQuery(lat=lat, lon=lon)
        response = await orchestrator.process_request(
            AgentType.WEATHER,
            weather_query.dict()
        )
        return response
    except Exception as e:
        logger.error(f"Error in get_weather: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemes", response_model=Dict[str, Any])
async def get_schemes(
    query: str
):
    """
    Get government schemes information
    """
    try:
        schemes_query = SchemesQuery(query=query)
        response = await orchestrator.process_request(
            AgentType.SCHEMES,
            schemes_query.dict()
        )
        return response
    except Exception as e:
        logger.error(f"Error in get_schemes: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents", response_model=List[str])
async def list_agents():
    """List all available agents"""
    return orchestrator.get_available_agents()
