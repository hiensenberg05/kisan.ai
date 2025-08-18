"""
Application configuration settings.

This module contains all the configuration settings for the Kisan.AI backend.
It loads environment variables and provides type-safe access to configuration values.
"""
import os
from typing import List, Optional, Any
from pydantic import AnyHttpUrl, validator, PostgresDsn
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    API_PREFIX: str = "/api/v1"
    API_VERSION: str = "1.0.0"
    PROJECT_NAME: str = "Kisan.AI Backend"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "False").lower() in ("true", "1", "t")
    
    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kisanai.db")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_kisanai.db")
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    WEATHER_API: Optional[str] = os.getenv("WEATHER_API")
    
    # External Services
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Model paths
    DISEASE_MODEL_PATH: str = os.getenv("DISEASE_MODEL_PATH", "models/disease_model.pth")
    
    # External API URLs and Keys
    PLANT_HEALTH_API_URL: Optional[str] = os.getenv("PLANT_HEALTH_API_URL")
    PLANT_HEALTH_API_KEY: Optional[str] = os.getenv("PLANT_HEALTH_API_KEY")
    AGNOMARKET_API_URL: Optional[str] = os.getenv("AGNOMARKET_API_URL")
    AGNOMARKET_API_KEY: Optional[str] = os.getenv("AGNOMARKET_API_KEY")
    APIFY_TOKEN: Optional[str] = os.getenv("APIFY_TOKEN")
    APIFY_INDIAMART_ACTOR: str = os.getenv("APIFY_INDIAMART_ACTOR", "natanielsantos/indiamart-scraper")
    SERP_PROVIDER: str = os.getenv("SERP_PROVIDER", "serpapi")
    SERPAPI_KEY: Optional[str] = os.getenv("SERPAPI_KEY")
    GOOGLE_CSE_API_KEY: Optional[str] = os.getenv("GOOGLE_CSE_API_KEY")
    GOOGLE_CSE_ENGINE_ID: Optional[str] = os.getenv("GOOGLE_CSE_ENGINE_ID")
    DATA_GOV_API_KEY: Optional[str] = os.getenv("DATA_GOV_API_KEY")
    
    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    
    # Rate limiting
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "100/minute")
    
    # Cache settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    
    # Email settings
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@kisanai.com")
    
    # Validation for CORS_ORIGINS
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database URL validation
    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"
    }

# Create settings instance
settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.DISEASE_MODEL_PATH), exist_ok=True)
