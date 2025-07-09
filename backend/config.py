import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT_ID: str = "projectkisan-465305"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # RAG Configuration
    RAG_CORPUS_ID: str = "4532873024948404224"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: str = "*"  # Can be comma-separated string or "*" for all origins
    CORS_ALLOW_CREDENTIALS: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Model Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEMPERATURE: float = 0.3
    GEMINI_MAX_TOKENS: int = 2048
    
    # RAG Configuration
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    
    # Speech Configuration
    SPEECH_LANGUAGE: str = "en-IN"
    SPEECH_SAMPLE_RATE: int = 16000
    
    # TTS Configuration
    TTS_LANGUAGE: str = "en-IN"
    TTS_VOICE_GENDER: str = "female"
    TTS_SPEAKING_RATE: float = 0.9
    
    # Market Data Configuration
    MARKET_CACHE_DURATION: int = 3600  # 1 hour
    MARKET_API_TIMEOUT: int = 10
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/webp"
    ALLOWED_AUDIO_TYPES: str = "audio/wav,audio/mp3,audio/ogg"
    
    @property
    def allowed_image_types_list(self) -> List[str]:
        """Convert ALLOWED_IMAGE_TYPES string to list"""
        return [img_type.strip() for img_type in self.ALLOWED_IMAGE_TYPES.split(",")]
    
    @property
    def allowed_audio_types_list(self) -> List[str]:
        """Convert ALLOWED_AUDIO_TYPES string to list"""
        return [audio_type.strip() for audio_type in self.ALLOWED_AUDIO_TYPES.split(",")]
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database Configuration (if needed in future)
    DATABASE_URL: Optional[str] = None
    
    # External APIs Configuration
    AGMARKNET_API_URL: str = "https://agmarknet.gov.in/api/v1"
    MANDI_API_URL: str = "https://api.data.gov.in/resource"
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = False
    METRICS_PORT: int = 9090
    
    # Development Configuration
    ENVIRONMENT: str = "development"
    ENABLE_SWAGGER: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Validation function
def validate_settings():
    """Validate critical settings"""
    required_settings = [
        "GOOGLE_CLOUD_PROJECT_ID",
        "GOOGLE_CLOUD_LOCATION",
        "RAG_CORPUS_ID"
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Missing required settings: {', '.join(missing_settings)}")
    
    return True

# Configuration for different environments
def get_environment_config():
    """Get configuration based on environment"""
    if settings.ENVIRONMENT == "production":
        return {
            "debug": False,
            "reload": False,
            "workers": 4,
            "log_level": "WARNING"
        }
    elif settings.ENVIRONMENT == "staging":
        return {
            "debug": False,
            "reload": False,
            "workers": 2,
            "log_level": "INFO"
        }
    else:  # development
        return {
            "debug": True,
            "reload": True,
            "workers": 1,
            "log_level": "DEBUG"
        }

# Export configuration
__all__ = ["settings", "validate_settings", "get_environment_config"] 