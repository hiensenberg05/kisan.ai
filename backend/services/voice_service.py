"""
Voice service that provides a unified interface for speech-to-text and text-to-speech functionality.
"""
import logging
from pathlib import Path
from typing import Optional

from modules.asr import transcribe_audio
from modules.tts import speak as synthesize_text_to_speech
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

class VoiceService:
    """Service for handling voice-related operations including speech recognition and synthesis."""
    
    def __init__(self):
        """Initialize the voice service."""
        logger.info("Initializing VoiceService")
    
    def transcribe(self, file_path: str) -> str:
        """
        Transcribe speech from an audio file to text.
        
        Args:
            file_path: Path to the audio file to transcribe
            
        Returns:
            str: The transcribed text
            
        Raises:
            FileNotFoundError: If the audio file doesn't exist
            AudioProcessingError: If there's an error processing the audio
            TranscriptionError: If the transcription fails
        """
        try:
            logger.info(f"Starting transcription of file: {file_path}")
            if not Path(file_path).exists():
                error_msg = f"Audio file not found: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
                
            text = transcribe_audio(file_path)
            logger.info(f"Successfully transcribed {file_path}, length: {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"Transcription failed for {file_path}: {str(e)}")
            raise
    
    def speak(self, text: str, output_path: str = "reply.mp3") -> str:
        """
        Convert text to speech and save as an audio file.
        
        Args:
            text: The text to convert to speech
            output_path: Path to save the output audio file (default: "reply.mp3")
            
        Returns:
            str: Path to the generated audio file
            
        Raises:
            TTSGenerationError: If speech synthesis fails
            FileOperationError: If file operations fail
        """
        try:
            logger.info(f"Starting text-to-speech conversion for {len(text)} characters")
            output_path = synthesize_text_to_speech(
                text=text,
                output_path=output_path
            )
            logger.info(f"Successfully generated speech file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Text-to-speech conversion failed: {str(e)}")
            raise

# Create a global instance for convenience
voice_service = VoiceService()

# For backward compatibility
def transcribe(file_path: str) -> str:
    """
    Transcribe speech from an audio file to text.
    
    Args:
        file_path: Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text
    """
    return voice_service.transcribe(file_path)

def speak(text: str, output_path: str = "reply.mp3") -> str:
    """
    Convert text to speech and save as an audio file.
    
    Args:
        text: The text to convert to speech
        output_path: Path to save the output audio file (default: "reply.mp3")
        
    Returns:
        str: Path to the generated audio file
    """
    return voice_service.speak(text, output_path)