import os
from typing import Any, Dict, Optional

# For Pydantic v2, use pydantic-settings package
try:
    # Try the new location (Pydantic v2)
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback to old location (Pydantic v1)
    from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Quiz Game API"
    API_V1_STR: str = ""
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # Database
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()