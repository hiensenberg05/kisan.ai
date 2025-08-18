"""
Digital Agronomist & Market Advisor - Core Orchestrator
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
from typing import Any, Dict, List, Optional, Union

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


@dataclass
class AgentConfig:
    path: str
    class_name: str
    description: str
    required_env: List[str] = field(default_factory=list)
    dependencies: List[AgentType] = field(default_factory=list)
    is_critical: bool = False


class Orchestrator:
    """
    Digital Agronomist & Market Advisor - Central Orchestrator
    """

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
        self.conversation_context = {}
        self._initialize_agents()

    def _get_agent_configs(self) -> Dict[AgentType, AgentConfig]:
        return {
            AgentType.MARKET: AgentConfig(
                path="agents.market_agent",
                class_name="MarketAgent",
                description="Provides real-time market prices, trends, and selling recommendations",
                required_env=["AGNOMARKET_API_KEY"],
                is_critical=False,
            ),
            AgentType.DISEASE: AgentConfig(
                path="agents.disease_agent",
                class_name="DiseaseAgent",
                description="Identifies plant diseases from images and descriptions",
                required_env=["PLANT_HEALTH_API_KEY", "PLANT_HEALTH_API_URL"],
                is_critical=True,
            ),
            AgentType.REMEDIES: AgentConfig(
                path="agents.remedies_agent",
                class_name="RemediesAgent",
                description="Suggests treatments and tracks their effectiveness",
                dependencies=[AgentType.DISEASE],
                is_critical=True,
            ),
            AgentType.SCHEMES: AgentConfig(
                path="agents.schemes_agent",
                class_name="SchemesAgent",
                description="Provides information about government schemes and subsidies",
                required_env=["GOOGLE_API_KEY"],
                is_critical=False,
            ),
            AgentType.WEATHER: AgentConfig(
                path="agents.weather_agent",
                class_name="WeatherAgent",
                description="Offers weather forecasts and farming-specific advice",
                required_env=["WEATHER_API"],
                is_critical=True,
            ),
            AgentType.VOICE: AgentConfig(
                path="agents.voice_agent",
                class_name="VoiceAgent",
                description="Handles voice interactions and translations",
                required_env=["GOOGLE_API_KEY"],
                is_critical=False,
            ),
        }

    def _initialize_agents(self):
        for agent_type in AgentType:
            self.agent_status[agent_type] = AgentStatus.INITIALIZING

        initialized = set()
        last_count = -1

        while len(initialized) < len(self.agent_configs) and len(initialized) != last_count:
            last_count = len(initialized)

            for agent_type, config in self.agent_configs.items():
                if agent_type in initialized:
                    continue

                deps_met = all(dep in initialized for dep in config.dependencies)
                if not deps_met:
                    continue

                missing_env = [env for env in config.required_env if not os.getenv(env)]
                if missing_env:
                    logger.warning(f"Skipping {agent_type.value} agent - Missing env vars: {missing_env}")
                    self.agent_status[agent_type] = AgentStatus.UNAVAILABLE
                    initialized.add(agent_type)
                    continue

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

        self._log_initialization_summary()

    def _log_initialization_summary(self):
        logger.info("\n" + "=" * 50)
        logger.info("AGENT INITIALIZATION SUMMARY")
        logger.info("=" * 50)

        for agent_type, status in self.agent_status.items():
            status_emoji = {
                AgentStatus.READY: "✅",
                AgentStatus.ERROR: "❌",
                AgentStatus.INITIALIZING: "🔄",
                AgentStatus.UNAVAILABLE: "⚠️",
            }.get(status, "❓")

            logger.info(f"{status_emoji} {agent_type.value.upper():<12} - {status.name}")

        logger.info("=" * 50 + "\n")

    # ---- keep all your process_request and workflows here ----
    # (disease, market, weather handling, etc.)


# -------------------------------------------------------
# ✅ ADK expects a global `agent` object
# -------------------------------------------------------

# Create orchestrator singleton
orchestrator = Orchestrator()

def get_orchestrator() -> Orchestrator:
    return orchestrator

# Wrap orchestrator into an ADK agent so it works in playground




# Export Orchestrator to ADK
agent = Agent(
    name="KisanOrchestrator",
    description="Central orchestrator coordinating specialized agents for Kisan AI.",
    instruction=Orchestrator.SYSTEM_PROMPT,
    tools=[],  # you can register orchestrator-level tools here if needed
)
