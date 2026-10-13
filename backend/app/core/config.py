# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_NAME: str = "VoyageAI"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str

    # JWT Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Email (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # External APIs (Phase 7+)
    OPENAI_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Gemini (Travel Twin)
    # Comma-separated, tried in order. If one is overloaded/unavailable, the next is used.
    # Can be changed from Render's Environment tab without touching code.
    GEMINI_MODELS: str = "gemini-3.7-flash,gemini-3.8-flash"
    GEMINI_TIMEOUT_SECONDS: int = 35  # per model attempt, so a hung call can't block for minutes

    @property
    def gemini_model_list(self) -> list[str]:
        return [m.strip() for m in self.GEMINI_MODELS.split(",") if m.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached so the .env file is only read once per app lifetime,
    not on every request that needs a config value.
    """
    return Settings()