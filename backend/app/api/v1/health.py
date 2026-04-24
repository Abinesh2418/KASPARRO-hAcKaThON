from fastapi import APIRouter
from app.schemas.preference import VisualSearchResponse
from app.core.config import settings
import httpx

router = APIRouter()


@router.get("/health")
async def health():
    groq_status = "configured" if settings.GROQ_API_KEY else "missing GROQ_API_KEY"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        ollama_status = "online" if r.status_code == 200 else f"error {r.status_code}"
    except Exception:
        ollama_status = "offline"

    return {"status": "ok", "groq": groq_status, "ollama": ollama_status}


@router.get("/")
async def root():
    return {
        "name": "Curio API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "visual_search": "/api/v1/visual-search",
            "products": "/api/v1/products",
            "preferences": "/api/v1/preferences/{session_id}",
        },
    }
