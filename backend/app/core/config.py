from pydantic_settings import BaseSettings
from typing import List
from dataclasses import dataclass


@dataclass
class MerchantConfig:
    name: str
    url: str
    access_token: str
    storefront_token: str

    @property
    def slug(self) -> str:
        return self.name.lower().replace(" ", "_")


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

    # Ollama (vision) — backend runs in Docker, so host.docker.internal reaches the local machine
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    OLLAMA_VISION_MODEL: str = "llama3.2-vision:latest"

    # Shopify — Multi-Merchant (up to 3 stores)
    SHOPIFY_STORE_URL_1: str = ""
    SHOPIFY_ACCESS_TOKEN_1: str = ""
    SHOPIFY_STOREFRONT_TOKEN_1: str = ""
    SHOPIFY_MERCHANT_NAME_1: str = "Kasparro"

    SHOPIFY_STORE_URL_2: str = ""
    SHOPIFY_ACCESS_TOKEN_2: str = ""
    SHOPIFY_STOREFRONT_TOKEN_2: str = ""
    SHOPIFY_MERCHANT_NAME_2: str = "Nova"

    SHOPIFY_STORE_URL_3: str = ""
    SHOPIFY_ACCESS_TOKEN_3: str = ""
    SHOPIFY_STOREFRONT_TOKEN_3: str = ""
    SHOPIFY_MERCHANT_NAME_3: str = "Indie"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def merchants(self) -> list[MerchantConfig]:
        """Return all configured Shopify merchants."""
        raw = [
            (self.SHOPIFY_STORE_URL_1, self.SHOPIFY_ACCESS_TOKEN_1, self.SHOPIFY_STOREFRONT_TOKEN_1, self.SHOPIFY_MERCHANT_NAME_1),
            (self.SHOPIFY_STORE_URL_2, self.SHOPIFY_ACCESS_TOKEN_2, self.SHOPIFY_STOREFRONT_TOKEN_2, self.SHOPIFY_MERCHANT_NAME_2),
            (self.SHOPIFY_STORE_URL_3, self.SHOPIFY_ACCESS_TOKEN_3, self.SHOPIFY_STOREFRONT_TOKEN_3, self.SHOPIFY_MERCHANT_NAME_3),
        ]
        return [
            MerchantConfig(name=name, url=url, access_token=token, storefront_token=storefront)
            for url, token, storefront, name in raw
            if url
        ]

    def get_merchant_by_url(self, url: str) -> MerchantConfig | None:
        for m in self.merchants:
            if m.url == url:
                return m
        return None


settings = Settings()
