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
    enable_event_bus_debug: bool = False
    
    # Event Broker Settings
    event_broker_type: str = "local" # local or redis
    redis_url: str = "redis://localhost:6379"
    postgres_url: Optional[str] = "postgresql://gideon:gideon_secret@localhost:5432/gideon_db"
    qdrant_url: str = "http://localhost:6333"
    node_id: str = "core_node_1"
    
    # Authentication Settings
    jwt_secret: str = os.environ.get("GIDEON_JWT_SECRET", "default_jwt_secret_change_in_production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 # 24 hours
    refresh_token_expire_days: int = 7
    disable_auth_for_dev: bool = False

    # Persistent settings storage path
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # Path to advanced multi-key env file (in project root / Api)
    credentials_file: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Api", "BAZIQHUE API KEY nvidia.env")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
