from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Tiba Mkononi"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_V1_PREFIX: str = "/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./tiba_mkononi.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Hugging Face / Google AI
    HF_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GEMMA_MODEL: str = "gemma-4-26b-a4b-it"

    # Security
    SECRET_KEY: str = "tiba-mkononi-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # File Storage
    STORAGE_ENDPOINT: str = "localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "tiba-mkononi-uploads"
    STORAGE_SECURE: bool = False

    # CORS
    CORS_ORIGINS: str = '["https://tiba-mkononi.vercel.app","http://localhost:3000","http://localhost:3001","*"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
