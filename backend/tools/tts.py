import vertexai
from google.cloud import texttospeech
import logging
from typing import Optional, Dict, Any, List
import io

from config import settings

logger = logging.getLogger(__name__)

class TTSHandler:
    """
    Text-to-Speech (TTS) handler using Google Cloud Text-to-Speech.
    Handles text-to-speech conversion for farmer responses.
    """
    
    def __init__(self):
        """Initialize TTS handler with Google Cloud Text-to-Speech client"""
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        
        # Initialize TTS client
        self.tts_client = texttospeech.TextToSpeechClient()
        
        # Supported voices for Indian farmers
        self.supported_voices = {
            "en-IN": {
                "male": "en-IN-Standard-A",
                "female": "en-IN-Standard-B"
            },
            "hi-IN": {
                "male": "hi-IN-Standard-A",
                "female": "hi-IN-Standard-B"
            },
            "kn-IN": {
                "male": "kn-IN-Standard-A",
                "female": "kn-IN-Standard-B"
            },
            "te-IN": {
                "male": "te-IN-Standard-A",
                "female": "te-IN-Standard-B"
            },
            "ta-IN": {
                "male": "ta-IN-Standard-A",
                "female": "ta-IN-Standard-B"
            },
            "mr-IN": {
                "male": "mr-IN-Standard-A",
                "female": "mr-IN-Standard-B"
            },
            "gu-IN": {
                "male": "gu-IN-Standard-A",
                "female": "gu-IN-Standard-B"
            },
            "bn-IN": {
                "male": "bn-IN-Standard-A",
                "female": "bn-IN-Standard-B"
            },
            "pa-IN": {
                "male": "pa-IN-Standard-A",
                "female": "pa-IN-Standard-B"
            },
            "ml-IN": {
                "male": "ml-IN-Standard-A",
                "female": "ml-IN-Standard-B"
            }
        }
        
        # Default configuration for agricultural TTS
        self.default_config = texttospeech.SynthesisInput(
            text=""
        )
        
        self.default_voice = texttospeech.VoiceSelectionParams(
            language_code="en-IN",
            name="en-IN-Standard-B",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        self.default_audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,  # Slightly slower for clarity
            pitch=0.0,
            volume_gain_db=0.0,
            effects_profile_id=["handset-class-device"]  # Optimized for mobile devices
        )
        
        logger.info("TTS Handler initialized with Indian language support")
    
    async def text_to_speech(
        self, 
        text: str, 
        language_code: str = "en-IN",
        voice_gender: str = "female"
    ) -> Optional[bytes]:
        """
        Convert text to speech using Google Cloud Text-to-Speech.
        
        Args:
            text: Text to convert to speech
            language_code: Language code (default: en-IN)
            voice_gender: Voice gender - 'male' or 'female' (default: female)
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            logger.info(f"Converting text to speech: {text[:50]}... (language: {language_code})")
            
            # Validate and clean text
            cleaned_text = await self._preprocess_text(text)
            
            if not cleaned_text:
                logger.error("Text preprocessing failed")
                return None
            
            # Get voice configuration
            voice_config = await self._get_voice_config(language_code, voice_gender)
            
            # Create synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_config,
                audio_config=self.default_audio_config
            )
            
            if response.audio_content:
                logger.info(f"Successfully generated audio: {len(response.audio_content)} bytes")
                return response.audio_content
            else:
                logger.error("No audio content in response")
                return None
                
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}", exc_info=True)
            return None
    
    async def _preprocess_text(self, text: str) -> Optional[str]:
        """Preprocess text for optimal speech synthesis"""
        try:
            if not text or len(text.strip()) == 0:
                return None
            
            # Clean and format text
            cleaned_text = text.strip()
            
            # Remove excessive whitespace
            cleaned_text = " ".join(cleaned_text.split())
            
            # Add pauses for better speech flow
            cleaned_text = cleaned_text.replace(".", ". ")
            cleaned_text = cleaned_text.replace("!", "! ")
            cleaned_text = cleaned_text.replace("?", "? ")
            
            # Remove multiple spaces
            cleaned_text = " ".join(cleaned_text.split())
            
            # Limit text length (TTS has limits)
            if len(cleaned_text) > 5000:
                cleaned_text = cleaned_text[:5000] + "..."
                logger.warning("Text truncated due to length limit")
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}", exc_info=True)
            return None
    
    async def _get_voice_config(self, language_code: str, voice_gender: str) -> texttospeech.VoiceSelectionParams:
        """Get voice configuration for specified language and gender"""
        try:
            # Check if language is supported
            if language_code not in self.supported_voices:
                logger.warning(f"Language {language_code} not supported, using en-IN")
                language_code = "en-IN"
            
            # Get voice name
            voices = self.supported_voices[language_code]
            voice_name = voices.get(voice_gender, voices["female"])  # Default to female
            
            # Create voice configuration
            voice_config = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if voice_gender == "female" else texttospeech.SsmlVoiceGender.MALE
            )
            
            return voice_config
            
        except Exception as e:
            logger.error(f"Error getting voice config: {e}", exc_info=True)
            # Return default voice config
            return self.default_voice
    
    async def text_to_speech_ssml(
        self, 
        ssml_text: str, 
        language_code: str = "en-IN",
        voice_gender: str = "female"
    ) -> Optional[bytes]:
        """
        Convert SSML text to speech for more control over speech synthesis.
        
        Args:
            ssml_text: SSML formatted text
            language_code: Language code
            voice_gender: Voice gender
            
        Returns:
            Audio bytes or None if failed
        """
        try:
            logger.info(f"Converting SSML to speech: {ssml_text[:50]}...")
            
            # Get voice configuration
            voice_config = await self._get_voice_config(language_code, voice_gender)
            
            # Create synthesis input with SSML
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
            
            # Perform synthesis
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice_config,
                audio_config=self.default_audio_config
            )
            
            if response.audio_content:
                logger.info(f"Successfully generated SSML audio: {len(response.audio_content)} bytes")
                return response.audio_content
            else:
                logger.error("No audio content in SSML response")
                return None
                
        except Exception as e:
            logger.error(f"Error in SSML text-to-speech conversion: {e}", exc_info=True)
            return None
    
    async def create_agricultural_response_audio(self, response_text: str, language_code: str = "en-IN") -> Optional[bytes]:
        """
        Create optimized audio response for agricultural queries.
        Adds pauses and emphasis for better understanding.
        """
        try:
            # Convert to SSML for better control
            ssml_text = await self._convert_to_agricultural_ssml(response_text, language_code)
            
            return await self.text_to_speech_ssml(ssml_text, language_code, "female")
            
        except Exception as e:
            logger.error(f"Error creating agricultural response audio: {e}", exc_info=True)
            # Fallback to regular TTS
            return await self.text_to_speech(response_text, language_code, "female")
    
    async def _convert_to_agricultural_ssml(self, text: str, language_code: str) -> str:
        """Convert text to SSML with agricultural-specific formatting"""
        try:
            # Start SSML
            ssml = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language_code}">'
            
            # Add agricultural-specific formatting
            # Add pauses after important points
            text = text.replace(".", ".<break time='500ms'/>")
            text = text.replace("!", "!<break time='300ms'/>")
            text = text.replace("?", "?<break time='300ms'/>")
            
            # Emphasize important agricultural terms
            agricultural_terms = [
                "disease", "pest", "fertilizer", "irrigation", "harvest",
                "market", "price", "government", "subsidy", "scheme",
                "treatment", "prevention", "recommendation", "important"
            ]
            
            for term in agricultural_terms:
                if term.lower() in text.lower():
                    text = text.replace(term, f'<emphasis level="moderate">{term}</emphasis>')
            
            # Add the text
            ssml += text
            
            # End SSML
            ssml += "</speak>"
            
            return ssml
            
        except Exception as e:
            logger.error(f"Error converting to agricultural SSML: {e}", exc_info=True)
            # Return simple SSML
            return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language_code}">{text}</speak>'
    
    async def get_available_voices(self, language_code: str = None) -> Dict[str, Any]:
        """Get available voices for specified language or all languages"""
        try:
            if language_code:
                if language_code in self.supported_voices:
                    return {
                        "language": language_code,
                        "voices": self.supported_voices[language_code]
                    }
                else:
                    return {"error": f"Language {language_code} not supported"}
            else:
                return {
                    "supported_languages": self.supported_voices,
                    "total_languages": len(self.supported_voices)
                }
                
        except Exception as e:
            logger.error(f"Error getting available voices: {e}", exc_info=True)
            return {"error": "An error occurred. Please try again later."}
    
    async def test_connection(self) -> bool:
        """Test TTS service connection"""
        try:
            # Create a simple test synthesis
            synthesis_input = texttospeech.SynthesisInput(text="Test")
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-IN",
                name="en-IN-Standard-B"
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # This should not raise an exception if service is accessible
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            logger.info("TTS connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"TTS connection test failed: {e}", exc_info=True)
            return False
    
    async def get_audio_format_info(self) -> Dict[str, Any]:
        """Get information about supported audio formats"""
        return {
            "supported_formats": [
                "MP3",
                "LINEAR16", 
                "OGG_OPUS",
                "MULAW"
            ],
            "default_format": "MP3",
            "default_speaking_rate": 0.9,
            "default_pitch": 0.0,
            "effects_profile": "handset-class-device"
        } 