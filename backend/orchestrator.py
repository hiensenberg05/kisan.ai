"""
Digital Agronomist & Market Advisor - Core Orchestrator

This module serves as the central nervous system of the Kisan AI platform, coordinating between
specialized agents to provide comprehensive farming assistance. It handles complex workflows
that may span multiple domains (disease detection, market analysis, weather, etc.) and ensures
seamless integration of different AI capabilities.
"""
from __future__ import annotations

import asyncio
import importlib
import json
import os
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, Union, Callable, Awaitable

from loguru import logger
from pydantic import BaseModel, Field, validator

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import agent types
from agents.disease_agent import DiseaseAgent
from agents.market_agent import MarketAgent
from agents.remedies_agent import RemediesAgent
from agents.schemes_agent import SchemesAgent
from agents.voice_agent import VoiceAgent
from agents.weather_agent import WeatherAgent

class AgentType(str, Enum):
    """Enumeration of available agent types with their roles and capabilities."""
    MARKET = "market"          # Handles market prices, trends, and selling recommendations
    DISEASE = "disease"        # Identifies plant diseases from images
    REMEDIES = "remedies"      # Suggests treatments and tracks their effectiveness
    SCHEMES = "schemes"        # Provides information about government schemes and subsidies
    WEATHER = "weather"        # Offers weather forecasts and farming-specific advice
    VOICE = "voice"            # Handles voice interactions and translations

class AgentStatus(Enum):
    """Status of an agent instance."""
    INITIALIZING = auto()
    READY = auto()
    ERROR = auto()
    UNAVAILABLE = auto()

@dataclass
class AgentConfig:
    """Configuration for an agent type."""
    path: str
    class_name: str
    description: str
    required_env: List[str] = field(default_factory=list)
    dependencies: List[AgentType] = field(default_factory=list)
    is_critical: bool = False

class Orchestrator:
    """
    Digital Agronomist & Market Advisor - Central Orchestrator
    
    This class serves as the brain of the Kisan AI platform, coordinating between specialized
    agents to provide comprehensive farming assistance. It handles complex workflows that may
    span multiple domains (disease detection, market analysis, weather, etc.) and ensures
    seamless integration of different AI capabilities.
    
    Key Responsibilities:
    1. Agent Lifecycle Management: Initialization, health checks, and error handling
    2. Workflow Orchestration: Coordinating multi-agent workflows
    3. Context Management: Maintaining conversation and user context
    4. Fallback Handling: Graceful degradation when services are unavailable
    5. Performance Monitoring: Tracking agent performance and response times
    """
    
    SYSTEM_PROMPT = """
    You are KisanMitra, an AI-powered Digital Agronomist & Market Advisor for Indian farmers.
    Your goal is to provide accurate, actionable, and culturally appropriate farming advice.
    
    Core Capabilities:
    1. Crop Health Analysis: Diagnose plant diseases and recommend treatments
    2. Market Intelligence: Provide real-time prices and selling recommendations
    3. Weather Advisory: Offer hyperlocal weather forecasts and farming advice
    4. Scheme Navigation: Explain government schemes and assist with applications
    5. Growth Monitoring: Track crop health and predict yields
    6. Financial Planning: Calculate costs and expected returns
    
    Response Guidelines:
    - Be concise, clear, and empathetic
    - Use simple language suitable for farmers
    - Include relevant emojis for better readability
    - Always cite sources and confidence levels
    - Acknowledge limitations when uncertain
    - Provide next steps or follow-up questions
    """
    
    def __init__(self):
        """Initialize the orchestrator with agent configurations."""
        self.agents: Dict[AgentType, Any] = {}
        self.agent_status: Dict[AgentType, AgentStatus] = {}
        self.agent_configs = self._get_agent_configs()
        self.conversation_context = {}
        self._initialize_agents()
    
    def _get_agent_configs(self) -> Dict[AgentType, AgentConfig]:
        """Define configurations for all available agents."""
        return {
            AgentType.MARKET: AgentConfig(
                path="agents.market_agent",
                class_name="MarketAgent",
                description="Provides real-time market prices, trends, and selling recommendations",
                required_env=["MARKET_API_KEY"],
                is_critical=False
            ),
            AgentType.DISEASE: AgentConfig(
                path="agents.disease_agent",
                class_name="DiseaseAgent",
                description="Identifies plant diseases from images and descriptions",
                required_env=["DISEASE_MODEL_ENDPOINT"],
                is_critical=True
            ),
            AgentType.REMEDIES: AgentConfig(
                path="agents.remedies_agent",
                class_name="RemediesAgent",
                description="Suggests treatments and tracks their effectiveness",
                dependencies=[AgentType.DISEASE],
                is_critical=True
            ),
            AgentType.SCHEMES: AgentConfig(
                path="agents.schemes_agent",
                class_name="SchemesAgent",
                description="Provides information about government schemes and subsidies",
                required_env=["SCHEMES_API_KEY"],
                is_critical=False
            ),
            AgentType.WEATHER: AgentConfig(
                path="agents.weather_agent",
                class_name="WeatherAgent",
                description="Offers weather forecasts and farming-specific advice",
                required_env=["WEATHER_API_KEY"],
                is_critical=True
            ),
            AgentType.VOICE: AgentConfig(
                path="agents.voice_agent",
                class_name="VoiceAgent",
                description="Handles voice interactions and translations",
                required_env=["SPEECH_KEY", "SPEECH_REGION"],
                is_critical=False
            )
        }
    
    def _initialize_agents(self):
        """Initialize all available agents with dependency resolution."""
        # Initialize status for all agents
        for agent_type in AgentType:
            self.agent_status[agent_type] = AgentStatus.INITIALIZING
        
        # Initialize agents in dependency order
        initialized = set()
        last_count = -1
        
        while len(initialized) < len(self.agent_configs) and len(initialized) != last_count:
            last_count = len(initialized)
            
            for agent_type, config in self.agent_configs.items():
                if agent_type in initialized:
                    continue
                    
                # Check if dependencies are met
                deps_met = all(dep in initialized for dep in config.dependencies)
                
                if not deps_met:
                    continue
                
                # Check required environment variables
                missing_env = [env for env in config.required_env if not os.getenv(env)]
                
                if missing_env:
                    logger.warning(f"Skipping {agent_type.value} agent - Missing env vars: {missing_env}")
                    self.agent_status[agent_type] = AgentStatus.UNAVAILABLE
                    initialized.add(agent_type)
                    continue
                
                # Try to initialize the agent
                try:
                    module = importlib.import_module(config.path)
                    agent_class = getattr(module, config.class_name)
                    self.agents[agent_type] = agent_class()
                    self.agent_status[agent_type] = AgentStatus.READY
                    initialized.add(agent_type)
                    logger.info(f"✅ Initialized {agent_type.value} agent")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {agent_type.value} agent: {str(e)}\n{traceback.format_exc()}")
                    self.agent_status[agent_type] = AgentStatus.ERROR
                    initialized.add(agent_type)
        
        # Log initialization summary
        self._log_initialization_summary()
    
    def _log_initialization_summary(self):
        """Log a summary of agent initialization status."""
        logger.info("\n" + "=" * 50)
        logger.info("AGENT INITIALIZATION SUMMARY")
        logger.info("=" * 50)
        
        for agent_type, status in self.agent_status.items():
            status_emoji = {
                AgentStatus.READY: "✅",
                AgentStatus.ERROR: "❌",
                AgentStatus.INITIALIZING: "🔄",
                AgentStatus.UNAVAILABLE: "⚠️"
            }.get(status, "❓")
            
            logger.info(f"{status_emoji} {agent_type.value.upper():<12} - {status.name}")
        
        logger.info("=" * 50 + "\n")
    
    async def process_request(
        self, 
        agent_type: Union[AgentType, str, None],
        request_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a request by routing it to the appropriate agent(s).
        
        Args:
            agent_type: Type of agent to handle the request (can be auto-detected if None)
            request_data: Input data for processing
            context: Optional conversation context
            
        Returns:
            Dict containing the agent's response with metadata
        """
        # Update conversation context
        self._update_context(context or {})
        
        # Auto-detect agent type if not specified
        if agent_type is None:
            agent_type = self._detect_agent_type(request_data)
        elif isinstance(agent_type, str):
            try:
                agent_type = AgentType(agent_type.lower())
            except ValueError:
                return self._create_error_response(
                    f"Invalid agent type: {agent_type}",
                    available_agents=[a.value for a in AgentType]
                )
        
        # Check agent availability
        if agent_type not in self.agents or self.agent_status.get(agent_type) != AgentStatus.READY:
            return self._handle_agent_unavailable(agent_type)
        
        # Process the request
        start_time = datetime.now()
        try:
            logger.info(f"🚀 Processing {agent_type.value} request")
            
            # Pre-process request data with context
            processed_data = self._preprocess_request(agent_type, request_data)
            
            # Route to the appropriate workflow handler
            if agent_type == AgentType.DISEASE and 'image' in processed_data:
                response = await self._handle_disease_workflow(processed_data)
            elif agent_type == AgentType.MARKET:
                response = await self._handle_market_workflow(processed_data)
            elif agent_type == AgentType.WEATHER:
                response = await self._handle_weather_workflow(processed_data)
            else:
                # Default single-agent processing
                agent = self.agents[agent_type]
                response = await agent.process(processed_data)
            
            # Post-process response
            processed_response = self._postprocess_response(agent_type, response)
            
            # Update context with new information
            self._update_agent_context(agent_type, processed_data, processed_response)
            
            # Log successful processing
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Completed {agent_type.value} request in {processing_time:.2f}s")
            
            return {
                "status": "success",
                "agent": agent_type.value,
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "data": processed_response,
                "context": self._get_relevant_context()
            }
            
        except Exception as e:
            return self._handle_processing_error(agent_type, e, start_time)
    
    async def _handle_disease_workflow(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the disease diagnosis and treatment workflow."""
        # 1. First, identify the disease
        disease_result = await self.agents[AgentType.DISEASE].identify(request_data)
        
        # 2. If we have a match, get treatment options
        remedies = {}
        if disease_result.get("confidence", 0) > 0.7:  # Only proceed with high confidence
            remedies = await self.agents[AgentType.REMEDIES].suggest_treatment(
                disease=disease_result["disease"],
                crop=request_data.get("crop"),
                severity=disease_result.get("severity", "medium")
            )
            
            # 3. Check for subsidies on recommended treatments
            if remedies.get("recommended_treatments"):
                for treatment in remedies["recommended_treatments"]:
                    if "chemical_name" in treatment:
                        subsidy_info = await self.agents[AgentType.SCHEMES].check_subsidy(
                            item=treatment["chemical_name"],
                            state=request_data.get("state")
                        )
                        treatment["subsidy_info"] = subsidy_info
        
        # 4. Get weather impact analysis
        weather_impact = {}
        if "location" in request_data:
            weather_impact = await self.agents[AgentType.WEATHER].get_disease_risk(
                location=request_data["location"],
                disease=disease_result.get("disease")
            )
        
        return {
            "diagnosis": disease_result,
            "treatments": remedies,
            "weather_impact": weather_impact,
            "next_steps": self._generate_disease_next_steps(disease_result, remedies)
        }
    
    async def _handle_market_workflow(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market analysis workflow."""
        # 1. Get current market prices
        market_data = await self.agents[AgentType.MARKET].get_prices(
            commodity=request_data.get("crop"),
            location=request_data.get("location"),
            timeframe=request_data.get("timeframe", "7d")
        )
        
        # 2. Get price trend analysis
        trend_analysis = await self.agents[AgentType.MARKET].analyze_trends(
            commodity=request_data.get("crop"),
            location=request_data.get("location")
        )
        
        # 3. Get selling recommendations
        recommendations = await self.agents[AgentType.MARKET].get_recommendations(
            commodity=request_data.get("crop"),
            quantity=request_data.get("quantity"),
            location=request_data.get("location")
        )
        
        # 4. Check for relevant government schemes
        schemes = {}
        if request_data.get("check_schemes", True):
            schemes = await self.agents[AgentType.SCHEMES].search({
                "query": f"subsidy for {request_data.get('crop')} farmers",
                "state": request_data.get("state")
            })
        
        return {
            "current_prices": market_data,
            "trend_analysis": trend_analysis,
            "recommendations": recommendations,
            "schemes": schemes.get("results", [])[:3],  # Top 3 relevant schemes
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _handle_weather_workflow(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather-related workflows."""
        # Get weather data
        weather_data = await self.agents[AgentType.WEATHER].get_forecast(
            location=request_data.get("location"),
            days=request_data.get("days", 7)
        )
        
        # Get farming advice based on weather
        farming_advice = await self.agents[AgentType.WEATHER].get_farming_advice(
            location=request_data.get("location"),
            crop=request_data.get("crop")
        )
        
        # Get disease risk assessment if crop is specified
        disease_risk = {}
        if "crop" in request_data:
            disease_risk = await self.agents[AgentType.DISEASE].assess_risk(
                crop=request_data["crop"],
                weather_conditions=weather_data.get("current", {})
            )
        
        return {
            "weather": weather_data,
            "farming_advice": farming_advice,
            "disease_risk": disease_risk,
            "alerts": self._generate_weather_alerts(weather_data)
        }
    
    def _detect_agent_type(self, request_data: Dict[str, Any]) -> AgentType:
        """Auto-detect the most appropriate agent based on request data."""
        # Check for image data (indicates disease detection)
        if "image" in request_data or "photo" in request_data:
            return AgentType.DISEASE
            
        # Check for market-related keywords
        market_keywords = ["price", "market", "sell", "buy", "mandi", "rate"]
        if any(kw in str(request_data).lower() for kw in market_keywords):
            return AgentType.MARKET
            
        # Check for weather-related keywords
        weather_keywords = ["weather", "rain", "temperature", "humidity", "forecast"]
        if any(kw in str(request_data).lower() for kw in weather_keywords):
            return AgentType.WEATHER
            
        # Check for scheme/subsidy related keywords
        scheme_keywords = ["scheme", "subsidy", "yojana", "loan", "financial aid"]
        if any(kw in str(request_data).lower() for kw in scheme_keywords):
            return AgentType.SCHEMES
            
        # Default to voice agent for general queries
        return AgentType.VOICE
    
    def _update_context(self, new_context: Dict[str, Any]):
        """Update the conversation context with new information."""
        self.conversation_context.update(new_context)
        
        # Enforce context size limits
        max_context_size = int(os.getenv("MAX_CONTEXT_SIZE", 4096))
        while len(json.dumps(self.conversation_context)) > max_context_size:
            # Remove oldest context items first
            oldest_key = next(iter(self.conversation_context))
            self.conversation_context.pop(oldest_key, None)
    
    def _get_relevant_context(self) -> Dict[str, Any]:
        """Get relevant context for the current conversation."""
        # Filter context to only include relevant information
        return {
            k: v for k, v in self.conversation_context.items()
            if not k.startswith('_')
        }
    
    def _preprocess_request(self, agent_type: AgentType, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess request data before passing to agent."""
        # Add common context to all requests
        processed = request_data.copy()
        
        # Add location from context if not provided
        if "location" not in processed and "location" in self.conversation_context:
            processed["location"] = self.conversation_context["location"]
        
        # Add language preference
        processed["language"] = self.conversation_context.get("language", "en")
        
        # Agent-specific preprocessing
        if agent_type == AgentType.DISEASE:
            # Ensure image data is properly formatted
            if "image" in processed and isinstance(processed["image"], str):
                # Handle base64 encoded images
                if processed["image"].startswith("data:image"):
                    processed["image"] = processed["image"].split(",", 1)[1]
        
        return processed
    
    def _postprocess_response(self, agent_type: AgentType, response: Any) -> Dict[str, Any]:
        """Post-process agent response before returning to client."""
        if isinstance(response, dict):
            processed = response.copy()
        else:
            processed = {"result": response}
        
        # Add agent-specific metadata
        processed["agent"] = agent_type.value
        processed["timestamp"] = datetime.utcnow().isoformat()
        
        return processed
    
    def _generate_disease_next_steps(self, diagnosis: Dict[str, Any], remedies: Dict[str, Any]) -> List[str]:
        """Generate actionable next steps based on disease diagnosis and remedies."""
        next_steps = []
        
        if diagnosis.get("confidence", 0) > 0.7:
            next_steps.append(f"Apply recommended treatments for {diagnosis['disease']}")
            
            if remedies.get("recommended_treatments"):
                next_steps.append("Purchase recommended treatments from your local agricultural store")
                
                # Check if any treatments have subsidies
                subsidized = any(t.get("subsidy_info") for t in remedies["recommended_treatments"])
                if subsidized:
                    next_steps.append("Check eligibility for government subsidies on recommended treatments")
            
            next_steps.extend([
                "Monitor crop for improvement over the next 3-5 days",
                "Take preventive measures to avoid spread to other plants",
                "Consult local agricultural expert if condition worsens"
            ])
        else:
            next_steps.extend([
                "The diagnosis confidence is low. Please provide clearer images if possible.",
                "Monitor the plant for any changes in symptoms",
                "Consider consulting a local agricultural expert for in-person diagnosis"
            ])
        
        return next_steps
    
    def _generate_weather_alerts(self, weather_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate weather alerts based on forecast data."""
        alerts = []
        
        # Check for extreme weather conditions
        current = weather_data.get("current", {})
        forecast = weather_data.get("forecast", [])
        
        # Current weather alerts
        if current.get("temp") > 40:  # High temperature
            alerts.append({
                "type": "heat_warning",
                "severity": "high",
                "message": "Extreme heat warning. Ensure proper irrigation and shading for crops.",
                "valid_until": (datetime.utcnow() + timedelta(hours=12)).isoformat()
            })
        
        # Forecast alerts
        for day in forecast[:3]:  # Next 3 days
            if day.get("precip_mm", 0) > 20:  # Heavy rain
                alerts.append({
                    "type": "heavy_rain",
                    "severity": "medium",
                    "message": f"Heavy rain expected on {day.get('date')}. Ensure proper drainage.",
                    "date": day.get("date")
                })
            
            if day.get("max_wind_kph", 0) > 30:  # High winds
                alerts.append({
                    "type": "high_wind",
                    "severity": "medium",
                    "message": f"High winds expected on {day.get('date')}. Secure loose items and protect delicate crops.",
                    "date": day.get("date")
                })
        
        return alerts
    
    def _create_error_response(
        self, 
        message: str, 
        status_code: int = 400,
        available_agents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a standardized error response."""
        error_info = {
            "status": "error",
            "error": message,
            "code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if available_agents:
            error_info["available_agents"] = available_agents
        
        return error_info
    
    def _handle_agent_unavailable(self, agent_type: AgentType) -> Dict[str, Any]:
        """Handle cases where the requested agent is not available."""
        status = self.agent_status.get(agent_type, AgentStatus.UNAVAILABLE)
        
        if status == AgentStatus.ERROR:
            return self._create_error_response(
                f"The {agent_type.value} agent encountered an error and is unavailable.",
                status_code=503
            )
        elif status == AgentStatus.UNAVAILABLE:
            return self._create_error_response(
                f"The {agent_type.value} agent is not available. Required configuration is missing.",
                status_code=503
            )
        else:
            return self._create_error_response(
                f"The {agent_type.value} agent is not available.",
                status_code=404
            )
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available agents with their status and capabilities.
        
        Returns:
            List of dictionaries containing agent information
        """
        agents_info = []
        for agent_type, agent in self.agents.items():
            agent_info = {
                "agent_id": agent_type.value,
                "name": agent_type.name.capitalize() + " Agent",
                "description": agent.__doc__ or f"Handles {agent_type.value} related tasks",
                "enabled": self.agent_status.get(agent_type) == AgentStatus.READY,
                "status": self.agent_status.get(agent_type, AgentStatus.UNAVAILABLE).name.lower()
            }
            agents_info.append(agent_info)
        return agents_info
        
    def _handle_processing_error(
        self, 
        agent_type: AgentType, 
        error: Exception,
        start_time: datetime
    ) -> Dict[str, Any]:
        """Handle errors that occur during request processing."""
        error_msg = f"Error processing {agent_type.value} request: {str(error)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Update agent status if it's in error state
        if self.agent_status.get(agent_type) != AgentStatus.ERROR:
            self.agent_status[agent_type] = AgentStatus.ERROR
            
        return self._create_error_response(
            message=error_msg,
            status_code=500,
            available_agents=[agt.value for agt in self.agents.keys()]
        )

# Create a singleton instance for easy import
orchestrator = Orchestrator()

def get_orchestrator() -> Orchestrator:
    """Get the shared orchestrator instance."""
    return orchestrator
