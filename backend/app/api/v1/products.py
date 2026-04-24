from fastapi import APIRouter, Query
from typing import Optional
from app.services import product_service

router = APIRouter()


@router.get("/products")
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
):
    products = product_service.search_products(category=category, limit=limit)
    return {"products": [p.model_dump() for p in products]}
