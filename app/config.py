# app/config.py
from pydantic_settings import BaseSettings  # Pydantic Settings class for env vars

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./quiz_app.db"  # Default database URL
    
    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"  # Specify .env file to load environment variables from

settings = Settings()  # This will load the settings into a `settings` object
