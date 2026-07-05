from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # API Keys
    nvidia_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Platform settings
    environment: str = "development"
    log_level: str = "INFO"

    # Persistent settings storage path
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
