# backend/api/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Query, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import base64
import logging
from loguru import logger
from datetime import datetime
from pydantic import BaseModel, Field

# Import schemas
from schemas.schemas import (
    DiagnoseRequest,
    MarketQuery,
    WeatherQuery,
    SchemesQuery,
    AgentResponse,
    SchemeSearchQuery
)

# Import agents and services
from agents.schemes_agent import schemes_agent, SchemeSearchQuery as SchemeQueryModel
from orchestrator import orchestrator, AgentType

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1",
    tags=["kisan-ai"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckResponse(BaseModel):
    status: str = Field(..., example="healthy")
    service: str = Field(..., example="kisan-ai-backend")
    version: str = Field(..., example="1.0.0")
    timestamp: str = Field(..., example="2023-01-01T00:00:00Z")

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    Returns basic service information and status.
    """
    return {
        "status": "healthy",
        "service": "kisan-ai-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

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

@router.post(
    "/schemes/search",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Search Government Schemes",
    description="Search for government schemes using natural language query"
)
async def search_schemes(
    query: SchemeQueryModel,
    state: Optional[str] = Query(None, description="Filter by state (e.g., 'Maharashtra')"),
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'Agriculture', 'Education')"),
    top_k: int = Query(5, description="Maximum number of results to return")
):
    """
    Search for government schemes based on natural language query and filters.
    
    Example queries:
    - "Schemes for small farmers"
    - "Education scholarships for farmers' children"
    - "Subsidy for organic farming"
    """
    try:
        search_params = {
            "query": query.query,
            "state": state,
            "category": category,
            "top_k": top_k
        }
        
        # Use the schemes agent for search
        results = await schemes_agent.search(search_params)
        
        if "error" in results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=results["error"]
            )
            
        return {
            "status": "success",
            "count": len(results),
            "schemes": results,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching schemes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching for schemes"
        )

@router.get(
    "/schemes/{scheme_id}",
    response_model=Dict[str, Any],
    summary="Get Scheme Details",
    description="Get detailed information about a specific scheme by ID"
)
async def get_scheme_details(scheme_id: str):
    """
    Retrieve detailed information about a specific government scheme by its ID.
    """
    try:
        scheme = await schemes_agent.get_scheme_details(scheme_id)
        
        if not scheme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme with ID {scheme_id} not found"
            )
            
        return {
            "status": "success",
            "data": scheme,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scheme details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching scheme details"
        )

@router.get(
    "/schemes",
    response_model=Dict[str, Any],
    summary="Get Schemes (Legacy)",
    deprecated=True,
    description="Legacy endpoint - Use /api/v1/schemes/search instead"
)
async def get_schemes_legacy(query: str):
    """
    Legacy endpoint for backward compatibility.
    Use /api/v1/schemes/search for more advanced search capabilities.
    """
    try:
        response = await schemes_agent.answer_query(query)
        return {
            "status": "success",
            "data": response,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error in get_schemes_legacy: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

class AgentInfo(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Display name of the agent")
    description: str = Field(..., description="Brief description of the agent's purpose")
    enabled: bool = Field(..., description="Whether the agent is currently enabled")

@router.get(
    "/agents",
    response_model=Dict[str, Any],
    summary="List Available Agents",
    description="Get a list of all available agents and their status"
)
async def list_agents():
    """
    Retrieve a list of all available agents in the system with their current status.
    """
    try:
        # Get the list of available agents with their status
        agents = orchestrator.get_available_agents()
        
        return {
            "status": "success",
            "count": len(agents),
            "agents": agents,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving agent information"
        )
