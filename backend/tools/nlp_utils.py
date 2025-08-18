"""
Natural Language Processing utilities for the farmer-assistant backend.
Handles text preprocessing, intent detection, and entity extraction.
"""
import re
import logging
from typing import Dict, List, Optional

from utils.logger import get_logger
from core.config import settings

# Initialize logger
logger = get_logger(__name__)

# Constants
FILLER_WORDS = {"uh", "hmm", "umm", "ah", "er", "like", "you know"}

INTENT_KEYWORDS = {
    "disease": {"disease", "infection", "crop health", "leaf spot", "blight", "wilt", "rot"},
    "remedies": {"pesticide", "fungicide", "remedy", "medicine", "treatment", "cure"},
    "market": {"market", "price", "trend", "sell", "mandi", "buy", "rate", "market rate"},
    "schemes": {"scheme", "subsidy", "government", "yojana", "support", "loan"},
    "weather": {"weather", "rain", "temperature", "forecast", "humidity", "wind"}
}

CROP_NAMES = {
    "wheat", "rice", "onion", "potato", "cotton", "maize", "sugarcane", 
    "soybean", "pulses", "millet", "barley", "jowar", "bajra"
}

def clean_text(text: str) -> str:
    """
    Clean and preprocess the input text.
    
    Args:
        text: Raw input text
        
    Returns:
        str: Cleaned text
        
    Raises:
        TextProcessingError: If text cleaning fails
    """
    try:
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
            
        logger.debug(f"Original text: {text}")
        
        # Convert to lowercase and strip whitespace
        cleaned = text.lower().strip()
        
        # Remove filler words
        words = [word for word in cleaned.split() if word not in FILLER_WORDS]
        cleaned = ' '.join(words)
        
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        logger.debug(f"Cleaned text: {cleaned}")
        return cleaned
        
    except Exception as e:
        logger.error(f"Error cleaning text: {str(e)}")
        raise TextProcessingError(f"Text cleaning failed: {str(e)}") from e

def detect_intent(text: str) -> str:
    """
    Detect the intent of the farmer's query.
    
    Args:
        text: Input text to analyze
        
    Returns:
        str: Detected intent (disease, remedies, market, schemes, weather, other)
        
    Raises:
        NLPAnalysisError: If intent detection fails
    """
    try:
        if not text:
            return "other"
            
        text = text.lower()
        logger.debug(f"Detecting intent for text: {text}")
        
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                logger.info(f"Detected intent: {intent}")
                return intent
                
        logger.info("No specific intent detected, defaulting to 'other'")
        return "other"
        
    except Exception as e:
        logger.error(f"Error detecting intent: {str(e)}")
        raise NLPAnalysisError(f"Intent detection failed: {str(e)}") from e

def extract_entities(text: str) -> Dict[str, str]:
    """
    Extract entities like crop names and locations from text.
    
    Args:
        text: Input text to analyze
        
    Returns:
        dict: Extracted entities with keys 'crop' and 'location'
        
    Raises:
        NLPAnalysisError: If entity extraction fails
    """
    entities = {"crop": None, "location": None}
    
    try:
        if not text:
            return entities
            
        logger.debug(f"Extracting entities from: {text}")
        
        # Extract crop names
        words = set(text.lower().split())
        for crop in CROP_NAMES:
            if crop in words:
                entities["crop"] = crop
                break
                
        # Extract location (simple regex for capitalized words)
        location_matches = re.findall(r'\b[A-Z][a-z]+\b', text)
        if location_matches:
            entities["location"] = location_matches[0]  # Take first match
            
        logger.info(f"Extracted entities: {entities}")
        return entities
        
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        raise NLPAnalysisError(f"Entity extraction failed: {str(e)}") from e

def analyze_input(text: str) -> Dict[str, any]:
    """
    Complete NLP analysis pipeline for farmer queries.
    
    Args:
        text: Raw input text from the user
        
    Returns:
        dict: Analysis result with keys:
            - cleaned_text: str
            - intent: str
            - entities: dict
            
    Raises:
        NLPAnalysisError: If analysis fails at any step
    """
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Input text is required and must be a string")
            
        logger.info(f"Starting NLP analysis for: {text[:50]}...")
        
        # Run the pipeline
        cleaned = clean_text(text)
        intent = detect_intent(cleaned)
        entities = extract_entities(cleaned)
        
        result = {
            "cleaned_text": cleaned,
            "intent": intent,
            "entities": entities
        }
        
        logger.info(f"Analysis completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"NLP analysis failed: {str(e)}")
        if not isinstance(e, (TextProcessingError, NLPAnalysisError)):
            raise NLPAnalysisError(f"Analysis failed: {str(e)}") from e
        raise