import re
import logging
import httpx
from app.core.config import settings
from app.schemas.product import Product

_CART_CREATE_MUTATION = """
mutation cartCreate($input: CartInput!) {
  cartCreate(input: $input) {
    cart {
      id
      checkoutUrl
      totalQuantity
      cost { totalAmount { amount currencyCode } }
    }
    userErrors { field message }
  }
}
"""


async def shopify_cart_create(
    merchant_url: str,
    storefront_token: str,
    cart_lines: list,
    api_version: str = "2024-10",
) -> dict:
    """
    Calls Shopify Storefront cartCreate mutation.
    Returns {"cart_id": ..., "checkout_url": ..., "total_amount": ..., "currency": ...}
    """
    endpoint = f"https://{merchant_url}/api/{api_version}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": storefront_token,
    }
    variables = {"input": {"lines": cart_lines}}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            endpoint,
            headers=headers,
            json={"query": _CART_CREATE_MUTATION, "variables": variables},
        )
    data = resp.json()

    if "errors" in data:
        raise Exception(f"Shopify cartCreate errors: {data['errors']}")

    cart_data = data["data"]["cartCreate"]
    if cart_data.get("userErrors"):
        raise Exception(f"Shopify cartCreate userErrors: {cart_data['userErrors']}")

    cart = cart_data["cart"]
    return {
        "cart_id": cart["id"],
        "checkout_url": cart["checkoutUrl"],
        "total_amount": float(cart["cost"]["totalAmount"]["amount"]),
        "currency": cart["cost"]["totalAmount"]["currencyCode"],
    }

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
        variants(first: 20) {
          edges {
            node {
              id
              price
              compareAtPrice
              selectedOptions { name value }
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

    variants_raw = node.get("variants", {}).get("edges", [])
    first_variant = variants_raw[0]["node"] if variants_raw else None
    price = float(first_variant["price"]) if first_variant else 0.0
    compare_raw = first_variant.get("compareAtPrice") if first_variant else None
    compare_at_price = float(compare_raw) if compare_raw else None

    # Variant GID for cartCreate (default = first variant)
    variant_id = first_variant["id"] if first_variant else None

    # All variants with size→GID mapping for size-specific checkout
    variants_list = []
    for edge in variants_raw:
        v = edge["node"]
        size_opt = next(
            (o["value"] for o in v.get("selectedOptions", []) if o["name"].lower() == "size"),
            None,
        )
        variants_list.append({"id": v["id"], "size": size_opt, "price": float(v["price"])})

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
        variant_id=variant_id,
        variants=variants_list,
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
