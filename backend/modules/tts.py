# backend/modules/tts.py
import base64
import os
from pathlib import Path
from typing import Optional, Union

import requests
from core.config import settings
from utils.logger import get_logger
from utils.errors import ConfigurationError, TextToSpeechError

logger = get_logger(__name__)

class TextToSpeech:
    """Text-to-Speech service using Google Cloud TTS API."""

    def __init__(self):
        self.settings = settings
        self.api_key = self.settings.GOOGLE_API_KEY
        self._validate_config()
        self.base_url = "https://texttospeech.googleapis.com/v1/text:synthesize"

    def _validate_config(self):
        """Validate required configuration."""
        if not self.api_key:
            raise ConfigurationError("GOOGLE_API_KEY is not configured.")

    def speak(
        self,
        text: str,
        output_path: Union[str, Path],
        language_code: str = "en-US",
        voice_name: str = "en-US-Wavenet-D",
    ) -> str:
        """
        Synthesizes speech from text and saves it to a file.

        Args:
            text: The text to synthesize.
            output_path: The path to save the output MP3 file.
            language_code: The language of the voice.
            voice_name: The name of the voice to use.

        Returns:
            The path to the output audio file.
        """
        logger.info(f"Synthesizing speech for text: '{text[:50]}...' to {output_path}")
        try:
            payload = {
                "input": {"text": text},
                "voice": {"languageCode": language_code, "name": voice_name},
                "audioConfig": {"audioEncoding": "MP3"},
            }

            response = requests.post(
                self.base_url, params={"key": self.api_key}, json=payload, timeout=30
            )
            response.raise_for_status()

            response_data = response.json()
            audio_content = base64.b64decode(response_data["audioContent"])

            # Ensure the output directory exists
            Path(output_path).parent.mkdir(exist_ok=True, parents=True)

            with open(output_path, "wb") as out_file:
                out_file.write(audio_content)

            logger.info(f"Speech audio saved to {output_path}")
            return str(output_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"TTS API request failed: {e}")
            raise TextToSpeechError(f"Failed to synthesize speech due to API error: {e}") from e
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to parse TTS API response: {e}")
            raise TextToSpeechError("Invalid response from TTS API.") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred during text-to-speech synthesis: {e}")
            raise TextToSpeechError(f"An unexpected error occurred: {e}") from e


text_to_speech = TextToSpeech()

def speak(
    text: str,
    output_path: Union[str, Path],
    language_code: str = "en-US",
    voice_name: str = "en-US-Wavenet-D",
) -> str:
    """Legacy function to synthesize speech."""
    return text_to_speech.speak(text, output_path, language_code, voice_name)
