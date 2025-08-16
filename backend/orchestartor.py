from typing import Dict, Any, List, Optional, Union
from enum import Enum
import importlib
import os
from loguru import logger
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import models and schemas
from schemas.schemas import DiagnoseRequest, OrchestratedResponse, MarketQuery

class AgentType(str, Enum):
    """Enumeration of available agent types."""
    MARKET = "market"
    DISEASE = "disease"
    REMEDIES = "remedies"
    SCHEMES = "schemes"
    WEATHER = "weather"
    VOICE = "voice"

class Orchestrator:
    """
    Central orchestrator that manages all agents and coordinates their interactions.
    Handles agent initialization, request routing, and response aggregation.
    """
    
    def __init__(self):
        self.agents: Dict[AgentType, Any] = {}
        self._initialize_agents()
        
        # Initialize direct agent instances for backward compatibility
        self.disease = self.agents.get(AgentType.DISEASE)
        self.remedies = self.agents.get(AgentType.REMEDIES)
        self.market = self.agents.get(AgentType.MARKET)
        self.weather = self.agents.get(AgentType.WEATHER)
        self.schemes = self.agents.get(AgentType.SCHEMES)
    
    def _initialize_agents(self):
        """Initialize all available agents dynamically."""
        agent_configs = {
            AgentType.MARKET: "agents.market_agent.MarketAgent",
            AgentType.DISEASE: "agents.disease_agent.DiseaseAgent",
            AgentType.REMEDIES: "agents.remedies_agent.RemediesAgent",
            AgentType.SCHEMES: "agents.schemes_agent.SchemesAgent",
            AgentType.WEATHER: "agents.weather_agent.WeatherAgent",
            AgentType.VOICE: "agents.voice_agent.VoiceAgent",
        }
        
        for agent_type, agent_path in agent_configs.items():
            try:
                module_path, class_name = agent_path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                agent_class = getattr(module, class_name)
                self.agents[agent_type] = agent_class()
                logger.info(f"Initialized {agent_type.value} agent")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Failed to initialize {agent_type.value} agent: {str(e)}")
    
    async def process_request(
        self, 
        agent_type: Union[AgentType, str],
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a request using the specified agent.
        
        Args:
            agent_type: Type of agent to handle the request
            request_data: Input data for the agent
            
        Returns:
            Dict containing the agent's response
        """
        if isinstance(agent_type, str):
            try:
                agent_type = AgentType(agent_type.lower())
            except ValueError:
                raise ValueError(f"Invalid agent type: {agent_type}. "
                               f"Available agents: {[a.value for a in AgentType]}")
        
        agent = self.agents.get(agent_type)
        if not agent:
            raise ValueError(f"Agent {agent_type} is not available")
        
        try:
            logger.info(f"Processing {agent_type.value} request with data: {request_data}")
            response = await agent.process(request_data)
            return {
                "status": "success",
                "agent": agent_type.value,
                "data": response
            }
        except Exception as e:
            logger.error(f"Error in {agent_type} agent: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "agent": agent_type.value,
                "error": str(e)
            }
    
    async def run_full_pipeline(
        self,
        diagnose_req: Optional[DiagnoseRequest] = None,
        market_q: Optional[MarketQuery] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        schemes_query: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline combining multiple agents.
        
        Args:
            diagnose_req: Plant disease diagnosis request
            market_q: Market data query
            lat: Latitude for weather data
            lon: Longitude for weather data
            schemes_query: Query for government schemes
            
        Returns:
            Combined response from all relevant agents
        """
        # Initialize default values
        diag = None
        prices = None
        mark = None
        weath = None
        sch = None
        
        # Run disease diagnosis if requested
        if diagnose_req and self.disease:
            try:
                diag = await self.disease.diagnose(diagnose_req.image_b64, diagnose_req.crop)
                if diag and hasattr(diag, 'disease') and self.remedies:
                    prices = await self.remedies.compare_prices(diag.disease)
            except Exception as e:
                logger.error(f"Error in disease diagnosis: {str(e)}")
        
        # Get market data if requested
        if market_q and self.market:
            try:
                mark = await self.market.insights(market_q)
            except Exception as e:
                logger.error(f"Error in market insights: {str(e)}")
        
        # Get weather data if location provided
        if lat is not None and lon is not None and self.weather:
            try:
                weath = await self.weather.advice(lat, lon)
            except Exception as e:
                logger.error(f"Error in weather service: {str(e)}")
        
        # Get scheme information if requested
        if schemes_query and self.schemes:
            try:
                sch = await self.schemes.answer(schemes_query)
            except Exception as e:
                logger.error(f"Error in schemes service: {str(e)}")
        
        # Return structured response
        return OrchestratedResponse(
            diagnose=diag,
            remedy_prices=prices,
            market=mark,
            weather=weath,
            schemes=sch
        )
