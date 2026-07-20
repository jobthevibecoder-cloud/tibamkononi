from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    APP_NAME: str = "Tiba Mkononi"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    API_V1_PREFIX: str = "/v1"

    DATABASE_URL: str = "sqlite:///./tiba_mkononi.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    HF_TOKEN: str = ""
    GEMMA_MODEL: str = "google/gemma-4-2b-it"

    SECRET_KEY: str = "tiba-mkononi-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    STORAGE_ENDPOINT: str = "localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET: str = "tiba-mkononi-uploads"
    STORAGE_SECURE: bool = False

    # Allow Vercel frontend + local dev
    CORS_ORIGINS: str = '["https://tiba-mkononi.vercel.app","http://localhost:3000","http://localhost:3001","https://tibamkononi.vercel.app","*"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
