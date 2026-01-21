"""
Configuration settings for Sakti-Link Edge Server
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Sakti-Link Edge Server"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    
    # Database
    DATABASE_PATH: str = "data/sakti_link.db"
    DATABASE_KEY: str = "your-encryption-key-change-this"  # Change in production!
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # AI Models
    MODELS_DIR: str = "models"
    WHISPER_MODEL: str = "openai/whisper-small"  # Lightweight for edge
    LLAMA_MODEL: str = "TheBloke/Llama-2-7B-Chat-GGUF"
    LLAMA_MODEL_FILE: str = "llama-2-7b-chat.Q4_K_M.gguf"
    SENTENCE_TRANSFORMER_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    
    # Bhashini API (for STT/TTS)
    BHASHINI_API_KEY: Optional[str] = None
    BHASHINI_API_URL: str = "https://api.bhashini.gov.in/v1"
    
    # Languages
    SUPPORTED_LANGUAGES: List[str] = [
        "hi",  # Hindi
        "bn",  # Bengali
        "ta",  # Tamil
        "te",  # Telugu
        "mr",  # Marathi
        "gu",  # Gujarati
        "kn",  # Kannada
        "ml",  # Malayalam
        "pa",  # Punjabi
        "or"   # Odia
    ]
    DEFAULT_LANGUAGE: str = "hi"
    
    # Voice Processing
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_FORMAT: str = "wav"
    MAX_AUDIO_LENGTH: int = 60  # seconds
    
    # Offline Mode
    OFFLINE_MODE: bool = True
    SYNC_INTERVAL: int = 3600  # seconds (1 hour)
    
    # Cloud Sync (Optional)
    CLOUD_API_URL: Optional[str] = None
    CLOUD_API_KEY: Optional[str] = None
    ENABLE_CLOUD_SYNC: bool = False
    
    # Privacy
    ANONYMIZE_USER_DATA: bool = True
    LOCAL_PROCESSING_ONLY: bool = True
    DATA_RETENTION_DAYS: int = 90
    
    # Learning
    LEARNING_CREDIT_INITIAL: int = 10
    LEARNING_CREDIT_PER_TEACH: int = 5
    LEARNING_CREDIT_PER_LEARN: int = -3
    NANO_LEARNING_DURATION: int = 120  # seconds (2 minutes)
    
    # Gigs
    GIG_SEARCH_RADIUS_KM: int = 10
    MAX_GIGS_PER_USER: int = 5
    
    # Legal
    LEGAL_TOPICS: List[str] = [
        "labor_rights",
        "safety_laws",
        "domestic_violence",
        "property_rights",
        "financial_rights",
        "workplace_harassment"
    ]
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"  # Change in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # Restrict in production
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/edge_server.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
Path(settings.MODELS_DIR).mkdir(parents=True, exist_ok=True)
Path("data").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)
Path("cache").mkdir(parents=True, exist_ok=True)
