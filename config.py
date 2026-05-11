"""FarmaTrack configuration — loads from .env"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "FarmaTrack"
    DATABASE_URL: str = "sqlite:///./farmatrack.db"
    API_BASE_URL: str = "http://localhost:8000"
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
