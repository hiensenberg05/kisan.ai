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

class VoiceAgent:
    """Voice Agent class for compatibility with orchestrator imports."""
    
    def __init__(self):
        self.agent = voice_agent
    
    async def process(self, request_data):
        """Process voice-related requests."""
        return {
            "message": "Voice processing functionality",
            "data": request_data
        }

voice_agent = Agent(
    name="FarmerVoiceAssistant",
    description="Agent for handling voice-based interactions with farmers.",
    instruction="""
    You are a helpful voice assistant for farmers.
    - Speak in a clear, friendly, and professional manner.
    - Keep responses concise and to the point.
    - Use simple language that's easy to understand.
    - Be patient and helpful with all queries.
    """,
    tools=[
        transcribe_audio,
        get_intent,
        generate_speech,
    ],
)