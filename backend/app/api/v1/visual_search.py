from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.preference import VisualSearchResponse
from app.services import ollama_service, shopify_service

router = APIRouter()

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/visual-search", response_model=VisualSearchResponse)
async def visual_search(file: UploadFile = File(...)):
    """
    Upload a fashion photo → vision model extracts style attributes → matched products returned.
    """
    print(f"\n{'='*60}")
    print(f"[VISUAL SEARCH] Request received | file: {file.filename} | type: {file.content_type}")

    if file.content_type not in _ALLOWED_TYPES:
        print(f"[VISUAL SEARCH] Rejected: invalid content type '{file.content_type}'")
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WEBP images accepted.")

    image_bytes = await file.read()
    print(f"[VISUAL SEARCH] Image read | size: {len(image_bytes)/1024:.1f} KB")

    if len(image_bytes) > _MAX_SIZE:
        print(f"[VISUAL SEARCH] Rejected: image too large ({len(image_bytes)/1024/1024:.1f} MB)")
        raise HTTPException(status_code=400, detail="Image must be under 5 MB.")

    attributes = await ollama_service.analyze_image(image_bytes)
    print(f"[VISUAL SEARCH] Attributes: {attributes}")

    search_queries: list[str] = []
    if attributes.get("description"):
        search_queries.append(attributes["description"])
    search_queries.extend(attributes.get("style", []))
    search_queries.extend(attributes.get("colors", []))
    if attributes.get("category"):
        search_queries.append(attributes["category"])
    search_queries.extend(attributes.get("occasion", []))
    deduped = list(dict.fromkeys(q for q in search_queries if q))

    print(f"[VISUAL SEARCH] Searching Shopify with queries: {deduped}")
    products = shopify_service.search_products(queries=deduped, limit=6)
    print(f"[VISUAL SEARCH] Matched {len(products)} products | titles: {[p.title for p in products]}")
    print(f"{'='*60}\n")
    return VisualSearchResponse(attributes=attributes, products=products)
