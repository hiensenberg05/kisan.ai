"""
Translation module for Kisan AI backend.
Supports multiple Indian languages including Hindi, Tamil, Telugu, etc.
"""

from typing import Dict, Optional, Union
from googletrans import Translator
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Language(Enum):
    """Supported languages for translation"""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    PUNJABI = "pa"
    MALAYALAM = "ml"
    ODIA = "or"
    URDU = "ur"

@dataclass
class TranslationResult:
    """Result of a translation operation"""
    text: str
    source_lang: str
    target_lang: str
    confidence: float = 1.0

class TranslationEngine:
    """Handles text translation between multiple languages"""
    
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {lang.value: lang.name for lang in Language}
        self._initialize_language_detection()
    
    def _initialize_language_detection(self):
        """Initialize language detection model"""
        try:
            # Test language detection
            self.translator.detect("test")
        except Exception as e:
            logger.warning(f"Error initializing translator: {e}")
            logger.warning("Falling back to offline mode with limited language support")
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code if detection is successful, None otherwise
        """
        if not text.strip():
            return None
            
        try:
            # Only consider the first 50 chars for detection to improve performance
            detection = self.translator.detect(text[:50])
            return detection.lang if hasattr(detection, 'lang') else None
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None
    
    def translate(
        self,
        text: str,
        target_lang: str,
        source_lang: Optional[str] = None
    ) -> TranslationResult:
        """
        Translate text to the target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'hi' for Hindi)
            source_lang: Optional source language code (auto-detected if None)
            
        Returns:
            TranslationResult object with translation and metadata
        """
        if not text.strip():
            return TranslationResult("", source_lang or "", target_lang, 1.0)
        
        try:
            # Validate target language
            if target_lang not in self.supported_languages:
                raise ValueError(f"Unsupported target language: {target_lang}")
            
            # Auto-detect source language if not provided
            if not source_lang:
                detected = self.detect_language(text)
                if detected and detected == target_lang:
                    return TranslationResult(text, detected, target_lang, 1.0)
                source_lang = detected or 'en'
            
            # Skip translation if source and target languages are the same
            if source_lang == target_lang:
                return TranslationResult(text, source_lang, target_lang, 1.0)
            
            # Perform translation
            translation = self.translator.translate(
                text,
                src=source_lang,
                dest=target_lang
            )
            
            return TranslationResult(
                text=translation.text,
                source_lang=source_lang,
                target_lang=target_lang,
                confidence=getattr(translation, 'confidence', 0.8)  # Default confidence if not provided
            )
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original text if translation fails
            return TranslationResult(
                text=text,
                source_lang=source_lang or "unknown",
                target_lang=target_lang,
                confidence=0.0
            )
    
    def translate_to_hindi(self, text: str) -> str:
        """Convenience method to translate text to Hindi"""
        return self.translate(text, Language.HINDI.value).text
    
    def translate_to_english(self, text: str) -> str:
        """Convenience method to translate text to English"""
        return self.translate(text, Language.ENGLISH.value).text
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names"""
        return self.supported_languages.copy()
    
    def is_language_supported(self, lang_code: str) -> bool:
        """Check if a language code is supported"""
        return lang_code in self.supported_languages

# Singleton instance
translator = TranslationEngine()

# Example usage
if __name__ == "__main__":
    # Example translations
    text = "Hello, how are you?"
    
    # Translate to Hindi
    hindi_translation = translator.translate(text, "hi")
    print(f"Hindi: {hindi_translation.text}")
    
    # Translate to Tamil
    tamil_translation = translator.translate(text, "ta")
    print(f"Tamil: {tamil_translation.text}")
    
    # Get list of supported languages
    print("\nSupported Languages:")
    for code, name in translator.get_supported_languages().items():
        print(f"{code}: {name}")