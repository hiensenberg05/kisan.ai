"""
Speech-to-Text module using Google Cloud Speech-to-Text API with API key authentication.
"""
import os
import io
import logging
from typing import Optional, BinaryIO, Union, Dict, Any
from pathlib import Path
import base64
import json
import requests

from utils.config import get_settings
from utils.errors import (
    AudioProcessingError,
    TranscriptionError,
    ConfigurationError
)

# Get logger
logger = logging.getLogger(__name__)

class SpeechToTextClient:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_API_KEY
        self.base_url = "https://speech.googleapis.com/v1/speech:recognize"
        
    async def transcribe_audio(
        self,
        audio_content: bytes,
        language_code: str = "en-US",
        sample_rate_hertz: int = 16000,
        enable_automatic_punctuation: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio using Google Cloud Speech-to-Text API with API key authentication.
        
        Args:
            audio_content: Raw audio content in bytes
            language_code: Language code (e.g., 'en-US')
            sample_rate_hertz: Sample rate of the audio in Hz
            enable_automatic_punctuation: Whether to enable automatic punctuation
            
        Returns:
            Dict containing the transcription results
        """
        if not self.api_key:
            raise ConfigurationError("GOOGLE_API_KEY is not configured")
            
        config = {
            "encoding": "LINEAR16",
            "sampleRateHertz": sample_rate_hertz,
            "languageCode": language_code,
            "enableAutomaticPunctuation": enable_automatic_punctuation
        }
        
        audio = {"content": audio_content.hex()}
        
        params = {"key": self.api_key}
        
        try:
            response = requests.post(
                self.base_url,
                params=params,
                json={"config": config, "audio": audio},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")

# Create a global instance for convenience
speech_client = SpeechToTextClient()

class SpeechToText:
    """Speech-to-Text service using Google Cloud Speech-to-Text API with API key."""
    
    def __init__(self):
        self.settings = get_settings()
        self._validate_config()
        self.api_key = self.settings.GOOGLE_API_KEY
        self.base_url = "https://speech.googleapis.com/v1/speech:recognize"
    
    def _validate_config(self):
        """Validate required configuration."""
        if not getattr(self.settings, 'GOOGLE_API_KEY', None):
            raise ConfigurationError("GOOGLE_API_KEY is not configured")
    
    def _get_audio_content(self, audio: Union[bytes, BinaryIO]) -> bytes:
        """Get audio content as bytes."""
        if isinstance(audio, bytes):
            return audio
        
        try:
            if hasattr(audio, 'read'):
                return audio.read()
            return audio
        except Exception as e:
            raise AudioProcessingError(f"Failed to read audio data: {str(e)}")
    
    def _get_recognition_config(self, language_code: Optional[str] = None) -> dict:
        """Create a recognition config dictionary with the specified settings."""
        language = language_code or getattr(self.settings, 'STT_LANGUAGE_CODE', 'en-US')
        enable_punctuation = getattr(self.settings, 'STT_ENABLE_AUTOMATIC_PUNCTUATION', True)
        
        return {
            "encoding": "LINEAR16",
            "sampleRateHertz": 16000,
            "languageCode": language,
            "enableAutomaticPunctuation": enable_punctuation,
            "model": "default"
        }
    
    def transcribe(
        self,
        audio: Union[bytes, BinaryIO, str, Path],
        language_code: Optional[str] = None
    ) -> str:
        """
        Transcribe audio to text using Google Cloud Speech-to-Text API with API key.
        
        Args:
            audio: Audio data as bytes, file-like object, or file path
            language_code: Language code in BCP-47 format (default: from settings)
            
        Returns:
            Transcribed text as a string
            
        Raises:
            AudioProcessingError: If there's an error processing the audio
            TranscriptionError: If the transcription fails
        """
        logger.info("Starting speech-to-text transcription")
        
        try:
            # Handle file path input
            if isinstance(audio, (str, Path)):
                if not os.path.isfile(audio):
                    raise AudioProcessingError(f"Audio file not found: {audio}")
                
                with open(audio, 'rb') as f:
                    audio_content = f.read()
            else:
                audio_content = self._get_audio_content(audio)
            
            # Prepare the request
            config = self._get_recognition_config(language_code)
            
            # Convert audio content to base64
            audio_data = {"content": base64.b64encode(audio_content).decode("utf-8")}
            
            # Prepare the request URL with API key
            url = f"{self.base_url}?key={self.api_key}"
            
            logger.debug("Sending request to Google Cloud Speech-to-Text API")
            
            # Make the API request
            response = requests.post(
                url,
                json={
                    "config": config,
                    "audio": audio_data
                },
                timeout=30
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            result = response.json()
            
            # Process the response
            if not result.get('results'):
                raise TranscriptionError("No transcription results returned")
            
            # Combine all results
            transcript = " ".join(
                alternative.get('transcript', '') 
                for result in result['results'] 
                for alternative in result.get('alternatives', [])
            ).strip()
            
            if not transcript:
                raise TranscriptionError("Empty transcription result")
            
            logger.info("Successfully completed speech-to-text transcription")
            return transcript
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg) from e
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(error_msg)
            if isinstance(e, (AudioProcessingError, TranscriptionError)):
                raise
            raise TranscriptionError(error_msg) from e

# Global instance for easier imports
speech_to_text = SpeechToText()

# For backward compatibility
def transcribe_audio(
    file_path: Union[str, Path],
    language_code: Optional[str] = None
) -> str:
    """
    Transcribe an audio file to text (legacy function).
    
    Args:
        file_path: Path to the audio file
        language_code: Language code in BCP-47 format
        
    Returns:
        Transcribed text as a string
    """
    return speech_to_text.transcribe(file_path, language_code)