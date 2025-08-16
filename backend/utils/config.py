# backend/config.py
from pydantic import BaseSettings, AnyHttpUrl
from functools import lru_cache

class Settings(BaseSettings):
    # FastAPI
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True

    # Google Cloud
    GOOGLE_CLOUD_PROJECT_ID: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str

    # RAG
    RAG_CORPUS_ID: str = ""
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7

    # Speech/TTS
    SPEECH_LANGUAGE: str = "en-IN"
    SPEECH_SAMPLE_RATE: int = 16000
    TTS_LANGUAGE: str = "en-IN"
    TTS_VOICE_GENDER: str = "female"
    TTS_SPEAKING_RATE: float = 0.9

    # External keys
    PLANT_HEALTH_API_URL: AnyHttpUrl = "https://api.plant.health/v1/diagnose"  # adjust if different
    PLANT_HEALTH_API_KEY: str

    APIFY_TOKEN: str
    APIFY_INDIAMART_ACTOR: str = "natanielsantos/indiamart-scraper"

    SERP_PROVIDER: str = "serpapi"  # or "google_cse"
    SERPAPI_KEY: str = ""
    GOOGLE_CSE_API_KEY: str = ""
    GOOGLE_CSE_ENGINE_ID: str = ""

    DATA_GOV_API_KEY: str = ""   # data.gov.in key (if you use official datasets)
    AGMARKNET_API_URL: AnyHttpUrl = "https://agmarknet.gov.in/api/v1"
    MANDI_API_URL: AnyHttpUrl = "https://api.data.gov.in/resource"

    OPENWEATHER_API_KEY: str
    GOOGLE_MAPS_API_KEY: str

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
