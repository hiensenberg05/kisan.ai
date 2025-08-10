import vertexai
from google.cloud import speech
import logging
from typing import Optional, Dict, Any, Tuple
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

            # Detect encoding and sample rate from raw bytes
            encoding, detected_sample_rate = self._detect_audio_encoding(processed_audio)

            # Build recognition config dynamically to match the actual encoding
            config_kwargs: Dict[str, Any] = dict(
                encoding=encoding,
                language_code=language_code,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=False,
                enable_word_confidence=True,
            )

            # Only set sample_rate_hertz when we know it (e.g., for LINEAR16/WAV)
            if detected_sample_rate:
                config_kwargs["sample_rate_hertz"] = detected_sample_rate
            # If encoding is OPUS and no sample rate provided, use 48000
            if not detected_sample_rate and encoding in (
                speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            ):
                config_kwargs["sample_rate_hertz"] = 48000

            # Use enhanced model when available
            # Use short model to reduce latency
            config_kwargs["model"] = "latest_short"

            config = speech.RecognitionConfig(**config_kwargs)

            # Create recognition audio object
            audio = speech.RecognitionAudio(content=processed_audio)

            # Perform recognition (first attempt)
            response = self.speech_client.recognize(config=config, audio=audio)

            # Extract transcribed text
            transcribed_text = await self._extract_transcription(response)

            if transcribed_text:
                logger.info(f"Successfully transcribed: {transcribed_text[:100]}...")
                return transcribed_text
            else:
                logger.warning("No transcription found; retrying with fallback config")

                # Fallback 1: try short model and explicit Opus sample rate
                fallback_kwargs = dict(config_kwargs)
                fallback_kwargs["model"] = "latest_short"
                # For Opus, set sample rate to 48000 if not set
                if encoding in (
                    speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                    speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                ) and not detected_sample_rate:
                    fallback_kwargs["sample_rate_hertz"] = 48000

                fallback_config = speech.RecognitionConfig(**fallback_kwargs)
                fallback_response = self.speech_client.recognize(config=fallback_config, audio=audio)
                transcribed_text = await self._extract_transcription(fallback_response)
                if transcribed_text:
                    logger.info("Transcription succeeded on fallback config")
                    return transcribed_text

                # Fallback 2: try language detection then re-run
                detected_language = await self.detect_language(processed_audio)
                if detected_language:
                    logger.info(f"Retrying with detected language: {detected_language}")
                    lang_kwargs = dict(fallback_kwargs)
                    lang_kwargs["language_code"] = detected_language
                    lang_config = speech.RecognitionConfig(**lang_kwargs)
                    lang_response = self.speech_client.recognize(config=lang_config, audio=audio)
                    transcribed_text = await self._extract_transcription(lang_response)
                    if transcribed_text:
                        logger.info("Transcription succeeded after language detection")
                        return transcribed_text

                logger.warning("No transcription after all fallbacks")
                return None
                
        except Exception as e:
            logger.error(f"Error in speech-to-text conversion: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def _preprocess_audio(self, audio_content: bytes) -> Optional[bytes]:
        """Preprocess audio content for optimal recognition.

        Accepts very small clips; downstream validation/logging will warn but not hard-fail.
        """
        try:
            # Allow short audio through; rely on recognition to handle or fail gracefully
            if not audio_content or len(audio_content) == 0:
                logger.warning("Empty audio content")
                return None

            # Some MediaRecorder implementations produce an initial small chunk before stop;
            # if combined chunks were not large, still try to process
            return audio_content

        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}", exc_info=True)
            return None
    
    async def _extract_transcription(self, response: speech.RecognizeResponse) -> Optional[str]:
        """Extract transcribed text from recognition response"""
        try:
            if not getattr(response, "results", None):
                return None

            transcriptions = []

            # In non-streaming RecognizeResponse, SpeechRecognitionResult has no `is_final`.
            # Safely collect the top alternative from each result.
            for result in response.results:
                try:
                    if getattr(result, "alternatives", None):
                        top_alt = result.alternatives[0]
                        if getattr(top_alt, "transcript", None):
                            transcriptions.append(top_alt.transcript)
                except Exception:
                    continue

            return " ".join([t for t in transcriptions if t]) if transcriptions else None
                
        except Exception as e:
            logger.error(f"Error extracting transcription: {e}", exc_info=True)
            return None
    
    async def detect_language(self, audio_content: bytes) -> Optional[str]:
        """Detect the language of the spoken audio"""
        try:
            logger.info("Detecting language from audio")
            
            # Detect encoding and sample rate to avoid mismatches (e.g., OPUS 48kHz)
            encoding, detected_sample_rate = self._detect_audio_encoding(audio_content)
            config_kwargs: Dict[str, Any] = dict(
                encoding=encoding,
                alternative_language_codes=list(self.supported_languages.keys()),
                enable_automatic_punctuation=True,
            )
            if detected_sample_rate:
                config_kwargs["sample_rate_hertz"] = detected_sample_rate
            config = speech.RecognitionConfig(**config_kwargs)
            
            audio = speech.RecognitionAudio(content=audio_content)
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Best-effort: SpeechRecognitionResult may expose language_code depending on API behavior
            try:
                if response.results:
                    language_code = getattr(response.results[0], "language_code", None)
                    if language_code:
                        logger.info(f"Detected language: {language_code}")
                        return language_code
            except Exception:
                pass
            
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

    def _detect_audio_encoding(self, audio_content: bytes) -> Tuple[speech.RecognitionConfig.AudioEncoding, Optional[int]]:
        """Detect audio encoding from magic bytes.

        Returns a tuple of (encoding, sample_rate_hertz or None).
        """
        try:
            # WAV (RIFF) header
            if audio_content.startswith(b"RIFF"):
                # Try to read sample rate from standard WAV header (bytes 24-27 little-endian)
                sample_rate = None
                try:
                    if len(audio_content) >= 28 and audio_content[8:12] == b"WAVE":
                        # Extract sample rate
                        sample_rate = int.from_bytes(audio_content[24:28], byteorder="little", signed=False)
                except Exception:
                    sample_rate = None
                return speech.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate or 16000

            # OGG/Opus
            if audio_content.startswith(b"OggS"):
                # Opus typically uses 48000 Hz
                return speech.RecognitionConfig.AudioEncoding.OGG_OPUS, 48000

            # WebM/Opus (EBML header)
            if audio_content.startswith(b"\x1A\x45\xDF\xA3"):
                # WebM/Opus typically uses 48000 Hz
                return speech.RecognitionConfig.AudioEncoding.WEBM_OPUS, 48000

            # MP3 (ID3 tag or frame sync 0xFF 0xFB)
            if audio_content.startswith(b"ID3") or audio_content.startswith(b"\xff\xfb"):
                return speech.RecognitionConfig.AudioEncoding.MP3, None

            # Fallback to LINEAR16 assumption if unknown
            logger.warning("Unknown audio header; defaulting to LINEAR16@16kHz")
            return speech.RecognitionConfig.AudioEncoding.LINEAR16, 16000
        except Exception as e:
            logger.error(f"Audio encoding detection failed: {e}")
            return speech.RecognitionConfig.AudioEncoding.LINEAR16, 16000
    
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