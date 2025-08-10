import re
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Language(Enum):
    HINGLISH = "hinglish"
    ENGLISH = "english"
    HINDI = "hindi"
    MIXED = "mixed"

@dataclass
class NLUResult:
    intent: str
    language: Language
    confidence: float
    entities: Dict[str, str]
    normalized_text: str
    original_text: str

class NLUEngine:
    """
    Natural Language Understanding engine optimized for Indian languages and Hinglish.
    Handles intent classification, entity extraction, and language detection.
    """
    
    def __init__(self):
        # Common Indian English/Hinglish words and their standard forms
        self.hinglish_english_map = {
            # Common Hinglish words
            'kyun': 'why', 'kaise': 'how', 'kya': 'what', 'hai': 'is', 'hain': 'are',
            'main': 'i', 'mera': 'my', 'tumhara': 'your', 'humara': 'our',
            'acha': 'good', 'thik': 'okay', 'theek': 'okay', 'nahi': 'no',
            'haan': 'yes', 'ji': '', 'bhai': 'brother', 'behen': 'sister',
            'kitna': 'how much', 'kab': 'when', 'kaun': 'who', 'kahan': 'where',
            # Common Indian English terms
            'prepone': 'bring forward', 'revert back': 'reply', 'do the needful': 'do what is needed',
            'pass out': 'graduate', 'shift': 'move', 'only': ''
        }
        
        # Common intents for agricultural domain
        self.intent_keywords = {
            'crop_disease': ['disease', 'pest', 'bug', 'rot', 'wilt', 'yellow', 'spots', 'fungus', 'infection'],
            'market_prices': ['price', 'rate', 'market', 'sell', 'buy', 'mandi', 'bazaar', 'cost'],
            'government_schemes': ['scheme', 'yojana', 'subsidy', 'loan', 'kcc', 'pmfby', 'government'],
            'weather': ['weather', 'rain', 'monsoon', 'temperature', 'humidity', 'forecast'],
            'cultivation': ['plant', 'sow', 'harvest', 'irrigation', 'fertilizer', 'pesticide']
        }
        
        # Common entities in agricultural domain
        self.entity_patterns = {
            'crop': r'\b(rice|wheat|maize|sugarcane|cotton|soybean|pulse|vegetable|fruit|mango|banana|apple|potato|tomato|onion|chilli|brinjal|okra|cauliflower|cabbage|paddy|bajra|jowar|ragi|mustard|groundnut|sesame|sunflower|safflower|castor)\b',
            'disease': r'\b(blight|rust|smut|wilt|mildew|rot|spot|virus|bacteria|fungus|pest|insect|bug)\b',
            'location': r'\b(in|at|near|around|close to|far from|distance to|distance from)\s+([A-Za-z\s]+)',
            'time': r'\b(today|tomorrow|yesterday|next week|last week|this month|next month|last month|in \d+ (days|weeks|months))\b'
        }
        
    def detect_language(self, text: str) -> Tuple[Language, float]:
        """Detect the primary language of the input text."""
        words = text.lower().split()
        total_words = len(words)
        if total_words == 0:
            return Language.ENGLISH, 0.0
            
        # Count Hinglish/Hindi words
        hinglish_count = sum(1 for word in words if word in self.hinglish_english_map)
        hinglish_ratio = hinglish_count / total_words
        
        if hinglish_ratio > 0.7:
            return Language.HINGLISH, hinglish_ratio
        elif hinglish_ratio > 0.3:
            return Language.MIXED, hinglish_ratio
        else:
            return Language.ENGLISH, 1.0 - hinglish_ratio
    
    def normalize_text(self, text: str) -> str:
        """Normalize Hinglish/Indian English to standard English."""
        words = text.lower().split()
        normalized_words = []
        
        for word in words:
            # Remove common Indian discourse markers
            if word in ['arre', 'arey', 'o', 'oye', 'ji', 'yaar', 'bhai', 'behen']:
                continue
                
            # Replace Hinglish words with English equivalents
            normalized_word = self.hinglish_english_map.get(word, word)
            if normalized_word:  # Skip empty replacements
                normalized_words.append(normalized_word)
        
        # Join and clean up the text
        normalized = ' '.join(normalized_words)
        
        # Fix common Indian English patterns
        normalized = re.sub(r'only$', '', normalized)  # Remove trailing 'only'
        normalized = re.sub(r'\s+', ' ', normalized).strip()  # Normalize spaces
        
        return normalized
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract key entities from the text."""
        entities = {}
        
        # Extract entities based on patterns
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if entity_type == 'location':
                    entities[entity_type] = match.group(2)  # Capture the location name
                else:
                    entities[entity_type] = match.group(0)
        
        return entities
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify the intent of the user's message."""
        text_lower = text.lower()
        max_score = 0
        best_intent = 'general_query'
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > max_score:
                max_score = score
                best_intent = intent
        
        # Calculate confidence (0.0 to 1.0)
        confidence = min(1.0, max_score / 3.0)
        
        return best_intent, confidence
    
    def process(self, text: str) -> NLUResult:
        """Process the input text and return NLU result."""
        # Detect language
        language, lang_confidence = self.detect_language(text)
        
        # Normalize text
        normalized_text = self.normalize_text(text)
        
        # Extract entities
        entities = self.extract_entities(normalized_text)
        
        # Classify intent
        intent, intent_confidence = self.classify_intent(normalized_text)
        
        # Calculate overall confidence
        confidence = (lang_confidence + intent_confidence) / 2.0
        
        return NLUResult(
            intent=intent,
            language=language,
            confidence=confidence,
            entities=entities,
            normalized_text=normalized_text,
            original_text=text
        )

# Singleton instance
nlu_engine = NLUEngine()

def process_text(text: str) -> Dict:
    """Process text using the NLU engine and return a dict result."""
    result = nlu_engine.process(text)
    return {
        'intent': result.intent,
        'language': result.language.value,
        'confidence': result.confidence,
        'entities': result.entities,
        'normalized_text': result.normalized_text,
        'original_text': result.original_text
    }
