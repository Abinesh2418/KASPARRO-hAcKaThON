from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    AZURE_OPENAI_MODEL: str = "gpt-4o"

    # Ollama (Gemma4 vision)
    OLLAMA_BASE_URL: str = "http://100.127.36.42:11434"
    OLLAMA_VISION_MODEL: str = "gemma4:26b"

    # Shopify — add when credentials arrive
    SHOPIFY_STORE_DOMAIN: str = ""
    SHOPIFY_STOREFRONT_TOKEN: str = ""

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
