"""
Configuration settings for the FastAPI backend
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://100.127.36.42:11434"
    DEFAULT_MODEL: str = "deepseek-r1:32b"
    REQUEST_TIMEOUT: int = 600  # 10 minutes timeout for long model responses
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
