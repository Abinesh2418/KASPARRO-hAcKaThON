from app.schemas.product import Product
from typing import List, Optional

MOCK_PRODUCTS: List[dict] = [
    {
        "id": "prod_001",
        "title": "Oversized Linen Blazer",
        "price": 149.00,
        "compare_at_price": 198.00,
        "images": ["https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=500&q=80"],
        "category": "outerwear",
        "colors": ["beige", "cream", "sand"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["minimal", "classic", "formal", "business", "sophisticated"],
        "tags": ["blazer", "workwear", "office", "linen", "versatile"],
        "description": "Relaxed-fit linen blazer with single-button closure. Effortlessly elevated for the office or weekend.",
        "rating": 4.7,
        "reviews_count": 312,
    },
    {
        "id": "prod_002",
        "title": "Classic White Oxford Shirt",
        "price": 89.00,
        "compare_at_price": 120.00,
        "images": ["https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=500&q=80"],
        "category": "tops",
        "colors": ["white", "light blue"],
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "style": ["classic", "formal", "business", "preppy"],
        "tags": ["shirt", "office", "versatile", "button-down", "cotton"],
        "description": "Premium 100% cotton oxford weave. A wardrobe cornerstone that works from boardroom to brunch.",
        "rating": 4.8,
        "reviews_count": 521,
    },
    {
        "id": "prod_003",
        "title": "High-Rise Straight Jeans",
        "price": 119.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=500&q=80"],
        "category": "bottoms",
        "colors": ["indigo", "blue", "dark wash"],
        "sizes": ["24", "25", "26", "27", "28", "29", "30", "32"],
        "style": ["casual", "classic", "streetwear"],
        "tags": ["jeans", "denim", "casual", "everyday", "high-rise"],
        "description": "The perfect high-rise straight cut in premium Japanese denim.",
        "rating": 4.6,
        "reviews_count": 843,
    },
    {
        "id": "prod_004",
        "title": "Slip Midi Dress",
        "price": 135.00,
        "compare_at_price": 175.00,
        "images": ["https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?auto=format&fit=crop&w=500&q=80"],
        "category": "dresses",
        "colors": ["champagne", "black", "dusty rose"],
        "sizes": ["XS", "S", "M", "L"],
        "style": ["romantic", "elegant", "minimal", "feminine"],
        "tags": ["dress", "date night", "satin", "slip", "evening"],
        "description": "Bias-cut satin slip dress with adjustable straps. Understated luxury from day to night.",
        "rating": 4.9,
        "reviews_count": 267,
    },
    {
        "id": "prod_005",
        "title": "Leather Moto Jacket",
        "price": 295.00,
        "compare_at_price": 380.00,
        "images": ["https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=500&q=80"],
        "category": "outerwear",
        "colors": ["black", "tan", "brown"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["edgy", "streetwear", "rock", "cool", "bold"],
        "tags": ["jacket", "leather", "moto", "edgy", "statement"],
        "description": "Genuine leather moto jacket with asymmetric zipper and quilted shoulder details.",
        "rating": 4.8,
        "reviews_count": 198,
    },
    {
        "id": "prod_006",
        "title": "Ribbed Knit Turtleneck",
        "price": 79.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=500&q=80"],
        "category": "tops",
        "colors": ["black", "cream", "camel", "grey"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["minimal", "classic", "cozy", "chic"],
        "tags": ["sweater", "knit", "turtleneck", "cozy", "winter"],
        "description": "Slim-fit ribbed turtleneck in ultra-soft merino blend. The essential layering piece.",
        "rating": 4.7,
        "reviews_count": 445,
    },
    {
        "id": "prod_007",
        "title": "Wide-Leg Trousers",
        "price": 109.00,
        "compare_at_price": 145.00,
        "images": ["https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=500&q=80"],
        "category": "bottoms",
        "colors": ["black", "ivory", "navy", "camel"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["minimal", "formal", "chic", "sophisticated"],
        "tags": ["trousers", "pants", "wide-leg", "office", "elegant"],
        "description": "Tailored wide-leg trousers in wrinkle-resistant fabric. Professional polish meets all-day comfort.",
        "rating": 4.5,
        "reviews_count": 376,
    },
    {
        "id": "prod_008",
        "title": "Mini Floral Sundress",
        "price": 89.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=500&q=80"],
        "category": "dresses",
        "colors": ["floral", "pink", "green", "white"],
        "sizes": ["XS", "S", "M", "L"],
        "style": ["bohemian", "feminine", "casual", "playful", "romantic"],
        "tags": ["dress", "floral", "summer", "beach", "vacation"],
        "description": "Breezy mini sundress with ruffle hem and adjustable tie straps.",
        "rating": 4.6,
        "reviews_count": 189,
    },
    {
        "id": "prod_009",
        "title": "Chunky Sole Loafers",
        "price": 159.00,
        "compare_at_price": 210.00,
        "images": ["https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=500&q=80"],
        "category": "shoes",
        "colors": ["black", "white", "brown"],
        "sizes": ["36", "37", "38", "39", "40", "41"],
        "style": ["streetwear", "minimal", "cool", "preppy"],
        "tags": ["shoes", "loafers", "chunky", "statement", "versatile"],
        "description": "Platform loafers with lug sole. Elevates any outfit — literally.",
        "rating": 4.8,
        "reviews_count": 321,
    },
    {
        "id": "prod_010",
        "title": "Classic White Sneakers",
        "price": 129.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=500&q=80"],
        "category": "shoes",
        "colors": ["white", "cream"],
        "sizes": ["36", "37", "38", "39", "40", "41", "42"],
        "style": ["casual", "minimal", "streetwear", "sporty"],
        "tags": ["sneakers", "shoes", "white", "everyday", "clean"],
        "description": "Minimalist leather sneakers with cushioned insole.",
        "rating": 4.9,
        "reviews_count": 1203,
    },
    {
        "id": "prod_011",
        "title": "Denim Jacket — Vintage Wash",
        "price": 99.00,
        "compare_at_price": 130.00,
        "images": ["https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=500&q=80"],
        "category": "outerwear",
        "colors": ["light blue", "indigo", "washed"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["casual", "streetwear", "classic", "americana"],
        "tags": ["jacket", "denim", "vintage", "casual", "layering"],
        "description": "Vintage-wash denim jacket with a lived-in feel. A true closet classic.",
        "rating": 4.6,
        "reviews_count": 612,
    },
    {
        "id": "prod_012",
        "title": "Structured Mini Handbag",
        "price": 189.00,
        "compare_at_price": 245.00,
        "images": ["https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=500&q=80"],
        "category": "accessories",
        "colors": ["black", "tan", "red"],
        "sizes": ["ONE SIZE"],
        "style": ["elegant", "classic", "chic", "formal"],
        "tags": ["bag", "handbag", "structured", "evening", "statement"],
        "description": "Top-handle mini bag in pebbled vegan leather.",
        "rating": 4.7,
        "reviews_count": 178,
    },
    {
        "id": "prod_013",
        "title": "Wrap Midi Skirt",
        "price": 85.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1583744946564-b52ac1c389c8?auto=format&fit=crop&w=500&q=80"],
        "category": "bottoms",
        "colors": ["terracotta", "olive", "navy"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["bohemian", "feminine", "romantic", "casual"],
        "tags": ["skirt", "wrap", "midi", "flowy", "summer"],
        "description": "Tie-front wrap midi skirt in crinkle fabric.",
        "rating": 4.5,
        "reviews_count": 234,
    },
    {
        "id": "prod_014",
        "title": "Cropped Athletic Hoodie",
        "price": 75.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=500&q=80"],
        "category": "tops",
        "colors": ["grey", "black", "pink", "mint"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["athletic", "sporty", "casual", "streetwear"],
        "tags": ["hoodie", "crop", "gym", "athletic", "cozy"],
        "description": "Cropped fleece hoodie with kangaroo pocket.",
        "rating": 4.6,
        "reviews_count": 489,
    },
    {
        "id": "prod_015",
        "title": "Tailored Blazer Dress",
        "price": 198.00,
        "compare_at_price": 260.00,
        "images": ["https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=500&q=80"],
        "category": "dresses",
        "colors": ["black", "camel", "grey"],
        "sizes": ["XS", "S", "M", "L"],
        "style": ["formal", "power", "chic", "business", "sophisticated"],
        "tags": ["dress", "blazer", "power dressing", "office", "statement"],
        "description": "Double-breasted blazer dress with notched lapels. Command the room.",
        "rating": 4.8,
        "reviews_count": 143,
    },
    {
        "id": "prod_016",
        "title": "Lace-Up Ankle Boots",
        "price": 179.00,
        "compare_at_price": 230.00,
        "images": ["https://images.unsplash.com/photo-1608256246200-53e635b5b65f?auto=format&fit=crop&w=500&q=80"],
        "category": "shoes",
        "colors": ["black", "brown", "tan"],
        "sizes": ["36", "37", "38", "39", "40", "41"],
        "style": ["edgy", "classic", "streetwear", "cool"],
        "tags": ["boots", "ankle", "lace-up", "fall", "versatile"],
        "description": "Combat-inspired ankle boots with lugged sole.",
        "rating": 4.7,
        "reviews_count": 267,
    },
    {
        "id": "prod_017",
        "title": "Silk Cami Top",
        "price": 95.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=500&q=80"],
        "category": "tops",
        "colors": ["champagne", "black", "ivory", "sage"],
        "sizes": ["XS", "S", "M", "L"],
        "style": ["elegant", "feminine", "romantic", "minimal"],
        "tags": ["top", "cami", "silk", "date night", "layering"],
        "description": "100% mulberry silk camisole with adjustable spaghetti straps.",
        "rating": 4.8,
        "reviews_count": 312,
    },
    {
        "id": "prod_018",
        "title": "Pleated Midi Skirt",
        "price": 79.00,
        "compare_at_price": 105.00,
        "images": ["https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=500&q=80"],
        "category": "bottoms",
        "colors": ["black", "burgundy", "forest green"],
        "sizes": ["XS", "S", "M", "L", "XL"],
        "style": ["feminine", "chic", "classic", "elegant"],
        "tags": ["skirt", "pleated", "midi", "office", "date"],
        "description": "Satin-finish pleated midi skirt with elasticated waist.",
        "rating": 4.6,
        "reviews_count": 198,
    },
    {
        "id": "prod_019",
        "title": "Oversized Graphic Tee",
        "price": 45.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=500&q=80"],
        "category": "tops",
        "colors": ["white", "black", "grey"],
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "style": ["streetwear", "casual", "cool", "relaxed"],
        "tags": ["tee", "graphic", "oversized", "casual", "streetwear"],
        "description": "Heavyweight oversized tee with vintage-inspired graphic print.",
        "rating": 4.5,
        "reviews_count": 678,
    },
    {
        "id": "prod_020",
        "title": "Gold Layered Necklace Set",
        "price": 55.00,
        "compare_at_price": None,
        "images": ["https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=500&q=80"],
        "category": "accessories",
        "colors": ["gold"],
        "sizes": ["ONE SIZE"],
        "style": ["feminine", "elegant", "minimal", "romantic"],
        "tags": ["jewelry", "necklace", "gold", "layered", "gift"],
        "description": "Set of 3 delicate gold-filled necklaces at varying lengths.",
        "rating": 4.9,
        "reviews_count": 423,
    },
]


def get_all_products() -> List[Product]:
    return [Product(**p) for p in MOCK_PRODUCTS]


def find_matching_products(
    query: str,
    response: str,
    preferences: dict,
    limit: int = 6,
) -> List[Product]:
    text = (query + " " + response).lower()
    scored: list[tuple[int, dict]] = []

    for p in MOCK_PRODUCTS:
        score = 0
        for style in p["style"]:
            if style in text:
                score += 3
            if style in preferences.get("style", []):
                score += 2
        for color in p["colors"]:
            if color in text:
                score += 2
            if color in preferences.get("colors", []):
                score += 2
        if p["category"] in text:
            score += 4
        for tag in p["tags"]:
            if tag in text:
                score += 1
        budget_max = preferences.get("budget_max")
        if budget_max and p["price"] > budget_max:
            score -= 10
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [Product(**p) for _, p in scored[:limit]]


def search_products(
    category: Optional[str] = None,
    colors: Optional[List[str]] = None,
    styles: Optional[List[str]] = None,
    limit: int = 20,
) -> List[Product]:
    results = MOCK_PRODUCTS
    if category:
        results = [p for p in results if p["category"] == category]
    if colors:
        results = [p for p in results if any(c in p["colors"] for c in colors)]
    if styles:
        results = [p for p in results if any(s in p["style"] for s in styles)]
    return [Product(**p) for p in results[:limit]]
