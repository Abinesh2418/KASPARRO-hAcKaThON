from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.preference import VisualSearchResponse
from app.schemas.product import Product
from app.services import ollama_service, product_service

router = APIRouter()

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/visual-search", response_model=VisualSearchResponse)
async def visual_search(file: UploadFile = File(...)):
    """
    Upload a fashion photo → Gemma4:26b extracts style attributes → matched products returned.
    """
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WEBP images accepted.")

    image_bytes = await file.read()
    if len(image_bytes) > _MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 5 MB.")

    attributes = await ollama_service.analyze_image(image_bytes)
    print(f"[visual-search] style attributes detected: {attributes}")

    mock_prefs = {
        "style": attributes.get("style", []),
        "colors": attributes.get("colors", []),
        "sizes": [],
        "budget_max": None,
        "occasions": attributes.get("occasion", []),
    }
    products = product_service.find_matching_products(
        query=attributes.get("description", ""),
        response="",
        preferences=mock_prefs,
        limit=6,
    )
    return VisualSearchResponse(attributes=attributes, products=products)
