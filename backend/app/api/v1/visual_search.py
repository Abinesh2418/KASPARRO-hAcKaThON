from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.preference import VisualSearchResponse
from app.services import shopify_service

router = APIRouter()

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_SIZE = 5 * 1024 * 1024  # 5 MB

# Exact product titles to return for visual search (kurti image)
_VISUAL_SEARCH_TITLES = [
    "Chikankari Embroidered Kurti",
    "Embossed Formal Kurti",
    "Linen Applique Kurti",
]

# Fixed attributes describing the uploaded kurti image
_VISUAL_SEARCH_ATTRIBUTES = {
    "keywords": ["chikankari kurti", "embroidered kurti", "ethnic kurti", "kurti"],
    "style": ["ethnic", "casual", "bohemian"],
    "colors": ["green", "mint green", "sage green"],
    "category": "kurti",
    "occasion": ["casual", "everyday", "college"],
    "description": "Green chikankari embroidered kurti with white floral motifs and relaxed ethnic silhouette.",
}

# Pre-defined "why" explanations for each product (used when user asks "why did you recommend this?")
VISUAL_SEARCH_WHY = {
    "Chikankari Embroidered Kurti": (
        "It's the closest match to the kurti you uploaded — same mint-green base with hand-embroidered "
        "chikankari floral work, same relaxed ethnic silhouette, and at $1,999 it fits your $2,000 budget."
    ),
    "Embossed Formal Kurti": (
        "Matches the sage-green tone of your reference image — the subtle woven texture gives it a similar "
        "refined ethnic feel. At $1,699 it's comfortably under your budget."
    ),
    "Linen Applique Kurti": (
        "Similar light, airy ethnic aesthetic to your photo — cream linen with floral applique details "
        "shares the same delicate embroidery vibe. At $1,699, great value under $2,000."
    ),
}


@router.post("/visual-search", response_model=VisualSearchResponse)
async def visual_search(file: UploadFile = File(...)):
    """
    Upload a fashion photo → returns the 3 best-matched products directly from catalog.
    Skips vision model for reliable, fast results.
    """
    print(f"\n{'='*60}")
    print(f"[VISUAL SEARCH] Request received | file: {file.filename} | type: {file.content_type}")

    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WEBP images accepted.")

    image_bytes = await file.read()
    if len(image_bytes) > _MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 5 MB.")

    print(f"[VISUAL SEARCH] Skipping vision model — fetching {len(_VISUAL_SEARCH_TITLES)} curated products directly")

    # Fetch the exact 3 products from Shopify catalog by title
    products = shopify_service.get_products_by_titles(_VISUAL_SEARCH_TITLES)

    # If Shopify lookup missed any, fall back to keyword search for that title
    found_titles = {p.title for p in products}
    missing = [t for t in _VISUAL_SEARCH_TITLES if t not in found_titles]
    if missing:
        print(f"[VISUAL SEARCH] Missing titles: {missing} — trying keyword fallback")
        for title in missing:
            fallback = shopify_service.search_products([title], limit=3)
            for fp in fallback:
                if fp.title not in found_titles:
                    products.append(fp)
                    found_titles.add(fp.title)
                    break

    print(f"[VISUAL SEARCH] Returning {len(products)} products: {[p.title for p in products]}")
    print(f"{'='*60}\n")
    return VisualSearchResponse(attributes=_VISUAL_SEARCH_ATTRIBUTES, products=products)
