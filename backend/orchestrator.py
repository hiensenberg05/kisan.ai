"""
Digital Agronomist & Market Advisor - Core Orchestrator
Enhanced with intelligent workflow routing and edge case handling
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
from typing import Any, Dict, List, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger
from dotenv import load_dotenv

# Google ADK
from google.adk import Agent

# Load environment variables
load_dotenv()

# Import agent types
from agents.disease_agent import DiseaseAgent
from agents.market_agent import MarketAgent
from agents.remedies_agent import RemediesAgent
from agents.schemes_agent import SchemesAgent
from agents.voice_agent import VoiceAgent
from agents.weather_agent import WeatherAgent


class AgentType(str, Enum):
    MARKET = "market"
    DISEASE = "disease"
    REMEDIES = "remedies"
    SCHEMES = "schemes"
    WEATHER = "weather"
    VOICE = "voice"


class AgentStatus(Enum):
    INITIALIZING = auto()
    READY = auto()
    ERROR = auto()
    UNAVAILABLE = auto()


class WorkflowType(str, Enum):
    DISEASE_DIAGNOSIS = "disease_diagnosis"
    MARKET_INQUIRY = "market_inquiry"
    WEATHER_CHECK = "weather_check"
    SCHEME_INFO = "scheme_info"
    GENERAL_ADVICE = "general_advice"


@dataclass
class AgentConfig:
    path: str
    class_name: str
    description: str
    required_env: List[str] = field(default_factory=list)
    dependencies: List[AgentType] = field(default_factory=list)
    is_critical: bool = False
    timeout: int = 30  # seconds


@dataclass
class WorkflowStep:
    agent_type: AgentType
    method: str
    required: bool = True
    timeout: int = 15
    fallback: Optional[Callable] = None


@dataclass
class RequestContext:
    user_id: str
    session_id: str
    location: Optional[Dict] = None
    crop_type: Optional[str] = None
    language: str = "en"
    timestamp: datetime = field(default_factory=datetime.now)


class Orchestrator:
    """Enhanced Digital Agronomist & Market Advisor Orchestrator"""

    SYSTEM_PROMPT = """
    You are KisanMitra, an AI-powered Digital Agronomist & Market Advisor for Indian farmers.
    Your goal is to provide accurate, actionable, and culturally appropriate farming advice.
    
    Core Capabilities:
    1. 🌱 Crop Health Analysis: Diagnose plant diseases and recommend treatments
    2. 📈 Market Intelligence: Provide real-time prices and selling recommendations
    3. 🌦️ Weather Advisory: Offer hyperlocal weather forecasts and farming advice
    4. 🏛️ Scheme Navigation: Explain government schemes and assist with applications
    5. 📊 Growth Monitoring: Track crop health and predict yields
    6. 💰 Financial Planning: Calculate costs and expected returns
    
    Response Guidelines:
    - Be concise, clear, and empathetic
    - Use simple language suitable for farmers
    - Include relevant emojis for better readability
    - Always cite sources and confidence levels
    - Acknowledge limitations when uncertain
    - Provide next steps or follow-up questions
    """

    def __init__(self):
        self.agents: Dict[AgentType, Any] = {}
        self.agent_status: Dict[AgentType, AgentStatus] = {}
        self.agent_configs = self._get_agent_configs()
        self.conversation_context: Dict[str, Any] = {}
        self.workflow_definitions = self._define_workflows()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._initialize_agents()

    def _get_agent_configs(self) -> Dict[AgentType, AgentConfig]:
        return {
            AgentType.MARKET: AgentConfig(
                path="agents.market_agent", class_name="MarketAgent",
                description="Market prices and trends", required_env=["AGNOMARKET_API_KEY"],
                is_critical=False, timeout=20
            ),
            AgentType.DISEASE: AgentConfig(
                path="agents.disease_agent", class_name="DiseaseAgent",
                description="Plant disease identification", 
                required_env=["PLANT_HEALTH_API_KEY", "PLANT_HEALTH_API_URL"],
                is_critical=True, timeout=25
            ),
            AgentType.REMEDIES: AgentConfig(
                path="agents.remedies_agent", class_name="RemediesAgent",
                description="Treatment suggestions", dependencies=[AgentType.DISEASE],
                is_critical=True, timeout=15
            ),
            AgentType.WEATHER: AgentConfig(
                path="agents.weather_agent", class_name="WeatherAgent",
                description="Weather forecasts and advice", required_env=["WEATHER_API"],
                is_critical=True, timeout=10
            ),
            AgentType.SCHEMES: AgentConfig(
                path="agents.schemes_agent", class_name="SchemesAgent",
                description="Government schemes info", required_env=["GOOGLE_API_KEY"],
                is_critical=False, timeout=20
            ),
            AgentType.VOICE: AgentConfig(
                path="agents.voice_agent", class_name="VoiceAgent",
                description="Voice and translation", required_env=["GOOGLE_API_KEY"],
                is_critical=False, timeout=15
            ),
        }

    def _define_workflows(self) -> Dict[WorkflowType, List[WorkflowStep]]:
        """Define workflow patterns for different request types"""
        return {
            WorkflowType.DISEASE_DIAGNOSIS: [
                WorkflowStep(AgentType.DISEASE, "diagnose_disease", required=True),
                WorkflowStep(AgentType.REMEDIES, "suggest_treatment", required=True),
                WorkflowStep(AgentType.WEATHER, "get_weather_impact", required=False)
            ],
            WorkflowType.MARKET_INQUIRY: [
                WorkflowStep(AgentType.MARKET, "get_market_prices", required=True),
                WorkflowStep(AgentType.WEATHER, "check_harvest_weather", required=False)
            ],
            WorkflowType.WEATHER_CHECK: [
                WorkflowStep(AgentType.WEATHER, "get_forecast", required=True)
            ],
            WorkflowType.SCHEME_INFO: [
                WorkflowStep(AgentType.SCHEMES, "get_schemes", required=True)
            ]
        }

    def _initialize_agents(self):
        """Initialize agents with dependency resolution and error handling"""
        for agent_type in AgentType:
            self.agent_status[agent_type] = AgentStatus.INITIALIZING

        initialized = set()
        max_attempts = len(self.agent_configs) * 2

        while len(initialized) < len(self.agent_configs) and max_attempts > 0:
            max_attempts -= 1
            progress_made = False

            for agent_type, config in self.agent_configs.items():
                if agent_type in initialized:
                    continue

                # Check dependencies
                if not all(dep in initialized for dep in config.dependencies):
                    continue

                # Check environment variables
                missing_env = [env for env in config.required_env if not os.getenv(env)]
                if missing_env:
                    logger.warning(f"🟡 {agent_type.value} agent unavailable - Missing: {missing_env}")
                    self.agent_status[agent_type] = AgentStatus.UNAVAILABLE
                    initialized.add(agent_type)
                    progress_made = True
                    continue

                # Initialize agent
                try:
                    module = importlib.import_module(config.path)
                    agent_class = getattr(module, config.class_name)
                    self.agents[agent_type] = agent_class()
                    self.agent_status[agent_type] = AgentStatus.READY
                    initialized.add(agent_type)
                    progress_made = True
                    logger.success(f"✅ {agent_type.value} agent ready")

                except Exception as e:
                    logger.error(f"❌ {agent_type.value} agent failed: {str(e)}")
                    self.agent_status[agent_type] = AgentStatus.ERROR
                    initialized.add(agent_type)
                    progress_made = True

            if not progress_made:
                break

        self._validate_critical_agents()
        self._log_initialization_summary()

    def _validate_critical_agents(self):
        """Ensure critical agents are available"""
        critical_agents = [t for t, c in self.agent_configs.items() if c.is_critical]
        unavailable_critical = [
            t for t in critical_agents 
            if self.agent_status[t] in [AgentStatus.ERROR, AgentStatus.UNAVAILABLE]
        ]
        
        if unavailable_critical:
            logger.warning(f"⚠️ Critical agents unavailable: {unavailable_critical}")

    def _log_initialization_summary(self):
        """Log agent initialization status"""
        logger.info("\n" + "=" * 50)
        logger.info("🤖 KISAN AI AGENT STATUS")
        logger.info("=" * 50)

        status_icons = {
            AgentStatus.READY: "✅", AgentStatus.ERROR: "❌",
            AgentStatus.INITIALIZING: "🔄", AgentStatus.UNAVAILABLE: "⚠️"
        }

        for agent_type, status in self.agent_status.items():
            icon = status_icons.get(status, "❓")
            logger.info(f"{icon} {agent_type.value.upper():<10} - {status.name}")

        logger.info("=" * 50)

    def _classify_request(self, query: str, context: RequestContext) -> WorkflowType:
        """Classify request type for workflow selection"""
        query_lower = query.lower()
        
        # Disease-related keywords
        disease_keywords = ["disease", "pest", "infection", "spots", "leaves", "fungus", "virus"]
        if any(keyword in query_lower for keyword in disease_keywords):
            return WorkflowType.DISEASE_DIAGNOSIS
            
        # Market-related keywords
        market_keywords = ["price", "market", "sell", "rate", "cost", "profit"]
        if any(keyword in query_lower for keyword in market_keywords):
            return WorkflowType.MARKET_INQUIRY
            
        # Weather-related keywords
        weather_keywords = ["weather", "rain", "temperature", "forecast", "climate"]
        if any(keyword in query_lower for keyword in weather_keywords):
            return WorkflowType.WEATHER_CHECK
            
        # Scheme-related keywords
        scheme_keywords = ["scheme", "subsidy", "government", "loan", "benefit"]
        if any(keyword in query_lower for keyword in scheme_keywords):
            return WorkflowType.SCHEME_INFO
            
        return WorkflowType.GENERAL_ADVICE

    async def _execute_workflow_step(self, step: WorkflowStep, query: str, 
                                   context: RequestContext, previous_results: Dict) -> Dict:
        """Execute a single workflow step with timeout and error handling"""
        agent = self.agents.get(step.agent_type)
        
        if not agent or self.agent_status[step.agent_type] != AgentStatus.READY:
            if step.required:
                raise Exception(f"{step.agent_type.value} agent not available")
            return {"status": "skipped", "reason": "agent_unavailable"}

        try:
            # Execute agent method with timeout
            method = getattr(agent, step.method)
            
            # Prepare arguments based on method signature
            kwargs = {"query": query, "context": context}
            if previous_results:
                kwargs["previous_results"] = previous_results
                
            result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self.executor, lambda: method(**kwargs)
                ),
                timeout=step.timeout
            )
            
            return {"status": "success", "data": result}
            
        except asyncio.TimeoutError:
            logger.warning(f"⏰ {step.agent_type.value} step timed out")
            if step.fallback:
                return step.fallback(query, context, previous_results)
            return {"status": "timeout"}
            
        except Exception as e:
            logger.error(f"💥 {step.agent_type.value} step failed: {str(e)}")
            if step.required:
                raise
            return {"status": "error", "message": str(e)}

    async def process_request(self, query: str, context: RequestContext, 
                            image_data: Optional[bytes] = None) -> Dict[str, Any]:
        """Main request processing with intelligent workflow routing"""
        try:
            # Classify request and select workflow
            workflow_type = self._classify_request(query, context)
            workflow_steps = self.workflow_definitions.get(workflow_type, [])
            
            logger.info(f"🎯 Processing {workflow_type.value} workflow")
            
            # Execute workflow steps
            results = {}
            previous_results = {}
            
            for i, step in enumerate(workflow_steps):
                logger.debug(f"📋 Executing step {i+1}/{len(workflow_steps)}: {step.agent_type.value}")
                
                try:
                    step_result = await self._execute_workflow_step(
                        step, query, context, previous_results
                    )
                    
                    results[step.agent_type.value] = step_result
                    
                    # Pass successful results to next steps
                    if step_result.get("status") == "success":
                        previous_results[step.agent_type.value] = step_result.get("data")
                        
                except Exception as e:
                    if step.required:
                        logger.error(f"💥 Critical step failed: {step.agent_type.value}")
                        return self._create_error_response(str(e), workflow_type)
                    else:
                        logger.warning(f"⚠️ Optional step failed: {step.agent_type.value}")
                        results[step.agent_type.value] = {"status": "failed", "error": str(e)}
            
            # Compile final response
            return self._compile_response(results, workflow_type, query, context)
            
        except Exception as e:
            logger.error(f"💥 Orchestrator error: {str(e)}\n{traceback.format_exc()}")
            return self._create_error_response(str(e))

    def _compile_response(self, results: Dict, workflow_type: WorkflowType, 
                         query: str, context: RequestContext) -> Dict[str, Any]:
        """Compile results into a coherent response"""
        successful_results = {
            k: v.get("data") for k, v in results.items() 
            if v.get("status") == "success"
        }
        
        if not successful_results:
            return self._create_error_response("No agents were able to process the request")
        
        response = {
            "status": "success",
            "workflow_type": workflow_type.value,
            "timestamp": datetime.now().isoformat(),
            "results": successful_results,
            "partial_results": len(successful_results) < len(results),
            "context": {
                "user_id": context.user_id,
                "session_id": context.session_id,
                "language": context.language
            }
        }
        
        # Add workflow-specific formatting
        if workflow_type == WorkflowType.DISEASE_DIAGNOSIS:
            response["summary"] = self._format_disease_response(successful_results)
        elif workflow_type == WorkflowType.MARKET_INQUIRY:
            response["summary"] = self._format_market_response(successful_results)
        elif workflow_type == WorkflowType.WEATHER_CHECK:
            response["summary"] = self._format_weather_response(successful_results)
        
        return response

    def _format_disease_response(self, results: Dict) -> str:
        """Format disease diagnosis workflow response"""
        parts = []
        
        if "disease" in results:
            disease_info = results["disease"]
            parts.append(f"🔍 Disease identified: {disease_info.get('name', 'Unknown')}")
            
        if "remedies" in results:
            remedy_info = results["remedies"]
            parts.append(f"💊 Treatment: {remedy_info.get('treatment', 'Consult expert')}")
            
        if "weather" in results:
            weather_info = results["weather"]
            parts.append(f"🌦️ Weather impact: {weather_info.get('advice', 'Monitor conditions')}")
            
        return " | ".join(parts) if parts else "Analysis completed"

    def _format_market_response(self, results: Dict) -> str:
        """Format market inquiry response"""
        if "market" in results:
            market_info = results["market"]
            price = market_info.get("price", "N/A")
            trend = market_info.get("trend", "stable")
            return f"📈 Current price: {price} | Trend: {trend}"
        return "Market information retrieved"

    def _format_weather_response(self, results: Dict) -> str:
        """Format weather check response"""
        if "weather" in results:
            weather_info = results["weather"]
            temp = weather_info.get("temperature", "N/A")
            condition = weather_info.get("condition", "Unknown")
            return f"🌤️ {condition} | Temperature: {temp}°C"
        return "Weather information retrieved"

    def _create_error_response(self, error_message: str, 
                             workflow_type: Optional[WorkflowType] = None) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "status": "error",
            "message": error_message,
            "workflow_type": workflow_type.value if workflow_type else None,
            "timestamp": datetime.now().isoformat(),
            "suggestion": "Please try again or contact support if the issue persists"
        }

    def get_agent_health(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        return {
            "orchestrator_status": "healthy",
            "agents": {
                agent_type.value: {
                    "status": status.name.lower(),
                    "available": status == AgentStatus.READY
                }
                for agent_type, status in self.agent_status.items()
            },
            "critical_agents_healthy": all(
                self.agent_status[t] == AgentStatus.READY
                for t, c in self.agent_configs.items() if c.is_critical
            ),
            "timestamp": datetime.now().isoformat()
        }


# -------------------------------------------------------
# Global orchestrator instance and ADK integration
# -------------------------------------------------------

# Create orchestrator singleton
orchestrator = Orchestrator()

def get_orchestrator() -> Orchestrator:
    return orchestrator

# Export to ADK
agent = Agent(
    name="KisanOrchestrator",
    description="Enhanced central orchestrator for Kisan AI with intelligent workflow routing.",
    instruction=Orchestrator.SYSTEM_PROMPT,
    tools=[],
)