"""FarmaTrack configuration — loads from .env or Streamlit secrets."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FarmaTrack"
    DATABASE_URL: str = "sqlite:///./farmatrack.db"
    API_BASE_URL: str = "http://localhost:8000"
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    GOOGLE_VISION_API_KEY: str = ""
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
