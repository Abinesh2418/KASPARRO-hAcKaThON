from fastapi import APIRouter
from app.api.v1 import chat, products, preferences, visual_search, health

router = APIRouter()

# Root + health (no prefix)
router.include_router(health.router, tags=["health"])

# All v1 routes under /api/v1
_v1 = APIRouter(prefix="/api/v1")
_v1.include_router(chat.router, tags=["chat"])
_v1.include_router(products.router, tags=["products"])
_v1.include_router(preferences.router, tags=["preferences"])
_v1.include_router(visual_search.router, tags=["visual-search"])

router.include_router(_v1)
