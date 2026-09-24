"""
app/config.py - Application Configuration & Settings.
Loads environment variables using pydantic-settings and python-dotenv.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ComicCraft – AI Comic Story Creator"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-3.6-flash"
    gemini_pro_model: str = "gemini-3.1-pro-preview"

    hf_api_key: str = ""
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    image_backend: str = "auto"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
