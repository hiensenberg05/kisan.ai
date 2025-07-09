import vertexai
from google.cloud import speech
import logging
from typing import Optional, Dict, Any
import io
import wave
import numpy as np

from config import settings

logger = logging.getLogger(__name__)

class ASRHandler:
    """
    Automatic Speech Recognition (ASR) handler using Google Cloud Speech-to-Text.
    Handles speech-to-text conversion for farmer voice queries.
    """
    
    def __init__(self):
        """Initialize ASR handler with Google Cloud Speech client"""
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        
        # Initialize Speech client
        self.speech_client = speech.SpeechClient()
        
        # Supported languages for Indian farmers
        self.supported_languages = {
            "en-IN": "English (India)",
            "hi-IN": "Hindi (India)",
            "kn-IN": "Kannada (India)",
            "te-IN": "Telugu (India)",
            "ta-IN": "Tamil (India)",
            "mr-IN": "Marathi (India)",
            "gu-IN": "Gujarati (India)",
            "bn-IN": "Bengali (India)",
            "pa-IN": "Punjabi (India)",
            "ml-IN": "Malayalam (India)"
        }
        
        # Default configuration for agricultural speech recognition
        self.default_config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-IN",
            alternative_language_codes=["hi-IN", "kn-IN", "te-IN"],
            enable_automatic_punctuation=True,
            enable_word_time_offsets=False,
            enable_word_confidence=True,
            model="latest_long",
            use_enhanced=True,
            speech_contexts=[{
                "phrases": [
                    "tomato", "rice", "wheat", "corn", "potato", "onion",
                    "disease", "pest", "fertilizer", "irrigation", "harvest",
                    "market", "price", "government", "subsidy", "scheme",
                    "farmer", "crop", "soil", "weather", "rain", "drought",
                    "mandi", "kisan", "krishi", "vyapar", "bazaar"
                ],
                "boost": 20.0
            }]
        )
        
        logger.info("ASR Handler initialized with Indian language support")
    
    async def speech_to_text(self, audio_content: bytes, language_code: str = "en-IN") -> Optional[str]:
        """
        Convert speech to text using Google Cloud Speech-to-Text.
        
        Args:
            audio_content: Raw audio bytes
            language_code: Language code for recognition (default: en-IN)
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            logger.info(f"Processing speech-to-text with language: {language_code}")
            
            # Validate audio format and convert if necessary
            processed_audio = await self._preprocess_audio(audio_content)
            
            if not processed_audio:
                logger.error("Failed to preprocess audio")
                return None
            
            # Update config with specified language
            config = self.default_config
            config.language_code = language_code
            
            # Create recognition audio object
            audio = speech.RecognitionAudio(content=processed_audio)
            
            # Perform recognition
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Extract transcribed text
            transcribed_text = await self._extract_transcription(response)
            
            if transcribed_text:
                logger.info(f"Successfully transcribed: {transcribed_text[:100]}...")
                return transcribed_text
            else:
                logger.warning("No transcription found in response")
                return None
                
        except Exception as e:
            logger.error(f"Error in speech-to-text conversion: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def _preprocess_audio(self, audio_content: bytes) -> Optional[bytes]:
        """Preprocess audio content for optimal recognition"""
        try:
            # Check if audio is already in the right format
            if len(audio_content) < 100:  # Too small
                logger.warning("Audio content too small")
                return None
            
            # For now, assume audio is already in LINEAR16 format
            # In a real implementation, you might need to convert from other formats
            return audio_content
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}", exc_info=True)
            return None
    
    async def _extract_transcription(self, response: speech.RecognizeResponse) -> Optional[str]:
        """Extract transcribed text from recognition response"""
        try:
            if not response.results:
                return None
            
            transcriptions = []
            
            for result in response.results:
                if result.is_final:
                    transcriptions.append(result.alternatives[0].transcript)
            
            if transcriptions:
                return " ".join(transcriptions)
            else:
                # If no final results, use the first alternative
                for result in response.results:
                    if result.alternatives:
                        transcriptions.append(result.alternatives[0].transcript)
                
                return " ".join(transcriptions) if transcriptions else None
                
        except Exception as e:
            logger.error(f"Error extracting transcription: {e}", exc_info=True)
            return None
    
    async def detect_language(self, audio_content: bytes) -> Optional[str]:
        """Detect the language of the spoken audio"""
        try:
            logger.info("Detecting language from audio")
            
            # Use language detection config
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                alternative_language_codes=list(self.supported_languages.keys()),
                enable_automatic_punctuation=True,
                model="latest_long",
                use_enhanced=True
            )
            
            audio = speech.RecognitionAudio(content=audio_content)
            response = self.speech_client.recognize(config=config, audio=audio)
            
            if response.results and response.results[0].alternatives:
                # Get the most likely language
                language_code = response.results[0].language_code
                logger.info(f"Detected language: {language_code}")
                return language_code
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}", exc_info=True)
            return None
    
    async def speech_to_text_with_language_detection(self, audio_content: bytes) -> Optional[str]:
        """Convert speech to text with automatic language detection"""
        try:
            # First detect the language
            detected_language = await self.detect_language(audio_content)
            
            if detected_language:
                # Use detected language for transcription
                return await self.speech_to_text(audio_content, detected_language)
            else:
                # Fallback to default language
                logger.warning("Language detection failed, using default language")
                return await self.speech_to_text(audio_content, "en-IN")
                
        except Exception as e:
            logger.error(f"Error in speech-to-text with language detection: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages
    
    async def test_connection(self) -> bool:
        """Test ASR service connection"""
        try:
            # Create a simple test audio (silence)
            test_audio = b'\x00' * 32000  # 1 second of silence at 16kHz
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-IN"
            )
            
            audio = speech.RecognitionAudio(content=test_audio)
            
            # This should not raise an exception if service is accessible
            response = self.speech_client.recognize(config=config, audio=audio)
            
            logger.info("ASR connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"ASR connection test failed: {e}", exc_info=True)
            return False
    
    async def get_audio_info(self, audio_content: bytes) -> Dict[str, Any]:
        """Get information about the audio content"""
        try:
            info = {
                "size_bytes": len(audio_content),
                "duration_estimate": len(audio_content) / 32000,  # Rough estimate for 16kHz
                "format": "Unknown"
            }
            
            # Try to detect format
            if audio_content.startswith(b'RIFF'):
                info["format"] = "WAV"
            elif audio_content.startswith(b'ID3') or audio_content.startswith(b'\xff\xfb'):
                info["format"] = "MP3"
            elif audio_content.startswith(b'OggS'):
                info["format"] = "OGG"
            else:
                info["format"] = "Raw Audio"
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting audio info: {e}", exc_info=True)
            return {"error": str(e)} 