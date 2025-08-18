# backend/agents/tools/voice_tools.py
from typing import Optional

from services.voice_service import transcribe, speak
from tools.nlp_utils import detect_intent
from utils.logger import get_logger

logger = get_logger(__name__)

async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text."""
    logger.info(f"Transcribing audio from: {audio_path}")
    try:
        # Note: voice_service.transcribe is synchronous, but we define the tool as async
        # to maintain consistency with the ADK framework, which works best with async tools.
        return transcribe(audio_path)
    except Exception as e:
        logger.error(f"Audio transcription failed in tool: {e}")
        raise

async def get_intent(text: str) -> str:
    """Detect intent from text."""
    logger.debug(f"Detecting intent for text: {text[:100]}...")
    try:
        # This is a synchronous function but defined as an async tool.
        return detect_intent(text)
    except Exception as e:
        logger.error(f"Intent detection failed in tool: {e}")
        return "other"

async def generate_speech(text: str, output_path: Optional[str] = None) -> str:
    """Generate speech from text."""
    output_path = output_path or "response.mp3"
    logger.info(f"Generating speech for text: '{text[:100]}...' to {output_path}")
    try:
        # This is a synchronous function but defined as an async tool.
        return speak(text, output_path)
    except Exception as e:
        logger.error(f"Speech generation failed in tool: {e}")
        raise
