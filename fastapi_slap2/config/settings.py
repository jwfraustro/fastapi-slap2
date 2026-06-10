"""Application settings for SLAP2."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    ROOT_PATH: str = os.getenv("ROOT_PATH", "")

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    """Return the cached settings instance."""
    return Settings()
