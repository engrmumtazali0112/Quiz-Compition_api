import os
from pydantic import BaseSettings
from typing import Optional

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Quiz Competition API"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quiz_app.db")
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    
    # Admin User Creation
    FIRST_ADMIN_USERNAME: Optional[str] = os.getenv("FIRST_ADMIN_USERNAME", "admin")
    FIRST_ADMIN_EMAIL: Optional[str] = os.getenv("FIRST_ADMIN_EMAIL", "admin@example.com")
    FIRST_ADMIN_PASSWORD: Optional[str] = os.getenv("FIRST_ADMIN_PASSWORD", "admin")
    
    # Quiz Settings
    DEFAULT_QUIZ_DURATION: int = 30  # minutes
    DEFAULT_PASS_PERCENTAGE: int = 70  # percentage
    
    # File Upload Settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()