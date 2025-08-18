"""Configuration settings for the application."""
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, Dict, Any
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Kisan.AI Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    # Google API
    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")
    
    # Speech-to-Text
    STT_LANGUAGE_CODE: str = "en-US"
    STT_ENABLE_AUTOMATIC_PUNCTUATION: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Storage
    UPLOAD_FOLDER: str = str(Path(__file__).parent.parent / "uploads")
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS: set[str] = {"wav", "mp3", "ogg", "flac"}
    
    # RAG
    RAG_CORPUS_ID: str = ""
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

    # Speech/TTS
    SPEECH_LANGUAGE: str = "en-IN"
    SPEECH_SAMPLE_RATE: int = 16000
    TTS_LANGUAGE: str = "en-IN"
    TTS_VOICE_GENDER: str = "female"
    TTS_SPEAKING_RATE: float = 0.9

    # External keys
    PLANT_HEALTH_API_URL: Optional[str] = "https://api.plant.health/v1/diagnose"
    PLANT_HEALTH_API_KEY: Optional[str] = None

    APIFY_TOKEN: Optional[str] = None
    APIFY_INDIAMART_ACTOR: str = "natanielsantos/indiamart-scraper"

    SERP_PROVIDER: str = "serpapi"  # or "google_cse"
    SERPAPI_KEY: str = ""
    GOOGLE_CSE_API_KEY: str = ""
    GOOGLE_CSE_ENGINE_ID: str = ""

    DATA_GOV_API_KEY: str = ""   # data.gov.in key (if you use official datasets)
    AGMARKNET_API_URL: Optional[str] = "https://agmarknet.gov.in/api/v1"
    MANDI_API_URL: Optional[str] = "https://api.data.gov.in/resource"

    OPENWEATHER_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None

    # CORS
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
