from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Tiba Mkononi"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://tiba_user:tiba_password@localhost:5432/tiba_mkononi"
    DATABASE_URL_SYNC: str = "postgresql://tiba_user:tiba_password@localhost:5432/tiba_mkononi"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Hugging Face
    HF_TOKEN: str = ""
    GEMMA_MODEL: str = "google/gemma-4-2b-it"

    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # File Storage
    STORAGE_ENDPOINT: str = "localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "tiba-mkononi-uploads"
    STORAGE_SECURE: bool = False

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:3001","https://tibamkononi.vercel.app"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
