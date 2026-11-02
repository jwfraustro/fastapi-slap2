"""Application settings for SLAP2."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    ROOT_PATH: str = os.getenv("ROOT_PATH", "")

    SERVICE_IVOID: str = "ivo://example.org/slap2"
    PUBLISHER: str = "FastAPI SLAP2 Example Service"
    LAST_UPDATE_DATE: str = "2026-11-02T00:00:00Z"

    DEFAULT_MAXREC: int = 1000
    MAX_RECORDS: int = 10000

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    """Return the cached settings instance."""
    return Settings()
