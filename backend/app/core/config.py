# app/core/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "VoyageAI"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str

    # JWT Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # External APIs (Phase 7+)
    OPENAI_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    """
    Cached so the .env file is only read once per app lifetime,
    not on every request that needs a config value.
    """
    return Settings()