import re
import logging
import httpx
from app.core.config import settings
from app.schemas.product import Product

logger = logging.getLogger(__name__)

_GRAPHQL_URL = f"https://{settings.SHOPIFY_STORE_URL}/admin/api/2026-04/graphql.json"

_QUERY = """
{
  products(first: 50) {
    edges {
      node {
        id
        title
        description
        productType
        tags
        images(first: 1) {
          edges { node { url } }
        }
        options {
          name
          values
        }
        variants(first: 1) {
          edges {
            node {
              price
              compareAtPrice
            }
          }
        }
      }
    }
  }
}
"""

_STYLE_KEYWORDS = {
    "minimal", "classic", "casual", "formal", "streetwear", "bohemian",
    "elegant", "sporty", "romantic", "chic", "edgy", "feminine", "preppy",
    "athletic", "vintage", "modern", "boho", "luxe",
}


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def _map_product(node: dict) -> Product:
    options = {opt["name"].lower(): opt["values"] for opt in node.get("options", [])}

    variants = node.get("variants", {}).get("edges", [])
    price = float(variants[0]["node"]["price"]) if variants else 0.0
    compare_raw = variants[0]["node"].get("compareAtPrice") if variants else None
    compare_at_price = float(compare_raw) if compare_raw else None

    images = [e["node"]["url"] for e in node.get("images", {}).get("edges", [])]

    colors = [c.lower() for c in options.get("color", options.get("colour", []))]
    sizes = options.get("size", [])

    tags = [t.lower() for t in node.get("tags", [])]
    category = (node.get("productType") or "general").lower()
    style = [t for t in tags if t in _STYLE_KEYWORDS] or ["casual"]
    description = _strip_html(node.get("description", ""))[:500]
    product_id = node["id"].split("/")[-1]

    return Product(
        id=product_id,
        title=node["title"],
        price=price,
        compare_at_price=compare_at_price,
        images=images or ["https://placehold.co/500x500?text=Product"],
        category=category,
        colors=colors or ["various"],
        sizes=sizes or ["ONE SIZE"],
        style=style,
        tags=tags,
        description=description,
        rating=4.5,
        reviews_count=0,
    )


_cache: list[Product] | None = None


def _get_products() -> list[Product]:
    global _cache
    if _cache is not None:
        print(f"[SHOPIFY] Cache hit -> {len(_cache)} products")
        return _cache

    print(f"[SHOPIFY] Cache miss -> fetching from Shopify: {_GRAPHQL_URL}")
    try:
        resp = httpx.post(
            _GRAPHQL_URL,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": settings.SHOPIFY_ACCESS_TOKEN,
            },
            json={"query": _QUERY},
            timeout=10.0,
        )
        resp.raise_for_status()
        edges = resp.json()["data"]["products"]["edges"]
        if edges:
            _cache = [_map_product(e["node"]) for e in edges]
            logger.info(f"Loaded {len(_cache)} products from Shopify")
            print(f"[SHOPIFY] Loaded {len(_cache)} products from Shopify API")
            return _cache
    except Exception as e:
        logger.warning(f"Shopify API unavailable, falling back to mock data: {e}")
        print(f"[SHOPIFY] API unavailable ({e}) -> falling back to mock products")

    from app.services import product_service
    _cache = product_service.get_all_products()
    print(f"[SHOPIFY] Using mock catalog -> {len(_cache)} products")
    return _cache


def search_products(queries: list[str], limit: int = 20) -> list[Product]:
    print(f"[SHOPIFY] Searching products | queries: {queries} | limit: {limit}")
    all_products = _get_products()
    results: list[Product] = []
    seen_ids: set[str] = set()

    for query in queries:
        if not query:
            continue
        q = query.lower()
        matched_this_query = 0
        for p in all_products:
            if p.id in seen_ids:
                continue
            if (
                q in p.title.lower()
                or q in p.category
                or any(q in tag for tag in p.tags)
                or any(q in s for s in p.style)
                or any(q in c for c in p.colors)
            ):
                results.append(p)
                seen_ids.add(p.id)
                matched_this_query += 1
        print(f"[SHOPIFY]   query '{q}' -> {matched_this_query} matches")

    print(f"[SHOPIFY] Total results: {len(results[:limit])} products returned")
    return results[:limit]


def get_product_by_id(product_id: str) -> Product | None:
    for p in _get_products():
        if p.id == product_id:
            return p
    return None


def get_all_products(limit: int = 20) -> list[Product]:
    return _get_products()[:limit]
