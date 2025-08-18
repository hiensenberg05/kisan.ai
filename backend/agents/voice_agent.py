"""
Voice Agent for handling voice-based interactions with farmers.
Uses Google ADK for agent orchestration and integrates with voice services.
"""
from google.adk import Agent
from agents.tools.voice_tools import (
    transcribe_audio,
    get_intent,
    generate_speech,
)
from agents.base_agent import BaseAgent


class VoiceAgent(BaseAgent):
    """Voice Agent with LLM integration for voice-based farmer interactions."""

    def __init__(self):
        system_prompt = """
        You are a helpful voice assistant for farmers in India.
        Your role is to understand and respond to voice queries in a clear,
        friendly, and culturally appropriate manner.
        Keep responses concise and easy to understand when spoken aloud.
        """
        super().__init__(
            name="FarmerVoiceAssistant",
            description="Agent for handling voice-based interactions with farmers.",
            system_prompt=system_prompt
        )

        # ✅ Define ADK agent here
        self.agent = Agent(
            name="FarmerVoiceAssistant",
            description="Agent for handling voice-based interactions with farmers.",
            instruction=system_prompt,
            tools=[
                transcribe_audio,
                get_intent,
                generate_speech,
            ],
        )

    async def process(self, request_data):
        """Process voice-related requests."""
        response = await self.agent.run(request_data)   # run ADK agent
        return response
