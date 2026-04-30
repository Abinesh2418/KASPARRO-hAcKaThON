"""
Multi-merchant Shopify service.

Fetches products from ALL configured Shopify stores in parallel and merges them
into a single searchable catalog. Each product is tagged with its merchant_name
and merchant_url so the cart and checkout agents can route correctly.

Product IDs are namespaced as "{merchant_slug}_{shopify_numeric_id}" to guarantee
uniqueness across stores (e.g. "nova_8123456", "indie_8123456").
"""
import re
import logging
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.core.config import settings, MerchantConfig
from app.schemas.product import Product

logger = logging.getLogger(__name__)

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


_PRODUCTS_QUERY = """
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


def _map_product(node: dict, merchant: MerchantConfig) -> Product:
    options = {opt["name"].lower(): opt["values"] for opt in node.get("options", [])}

    variants_raw = node.get("variants", {}).get("edges", [])
    first_variant = variants_raw[0]["node"] if variants_raw else None
    price = float(first_variant["price"]) if first_variant else 0.0
    compare_raw = first_variant.get("compareAtPrice") if first_variant else None
    compare_at_price = float(compare_raw) if compare_raw else None
    variant_id = first_variant["id"] if first_variant else None

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

    # Namespace ID to avoid collisions across stores: "{slug}_{numeric}"
    numeric_id = node["id"].split("/")[-1]
    product_id = f"{merchant.slug}_{numeric_id}"

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
        merchant_name=merchant.name,
        merchant_url=merchant.url,
    )


def _fetch_store_products(merchant: MerchantConfig) -> list[Product]:
    """Synchronously fetch all products from a single Shopify store."""
    url = f"https://{merchant.url}/admin/api/2026-04/graphql.json"
    print(f"[SHOPIFY] Fetching products from {merchant.name} ({merchant.url})")
    try:
        resp = httpx.post(
            url,
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": merchant.access_token,
            },
            json={"query": _PRODUCTS_QUERY},
            timeout=10.0,
        )
        resp.raise_for_status()
        edges = resp.json()["data"]["products"]["edges"]
        if edges:
            products = [_map_product(e["node"], merchant) for e in edges]
            print(f"[SHOPIFY] {merchant.name}: loaded {len(products)} products")
            return products
    except Exception as e:
        logger.warning(f"[SHOPIFY] {merchant.name} API failed: {e}")
        print(f"[SHOPIFY] {merchant.name}: API failed ({e})")
    return []


# Combined product cache across all merchants
_all_products_cache: list[Product] | None = None


def _get_all_products() -> list[Product]:
    """Fetch and cache products from all configured merchants in parallel."""
    global _all_products_cache

    if _all_products_cache is not None:
        print(f"[SHOPIFY] Cache hit -> {len(_all_products_cache)} products total")
        return _all_products_cache

    merchants = settings.merchants
    if not merchants:
        print(f"[SHOPIFY] No merchants configured -> using mock catalog")
        from app.services import product_service
        _all_products_cache = product_service.get_all_products()
        return _all_products_cache

    print(f"[SHOPIFY] Fetching from {len(merchants)} merchant(s) in parallel...")
    all_products: list[Product] = []

    # Parallel fetch from all stores
    with ThreadPoolExecutor(max_workers=len(merchants)) as pool:
        futures = {pool.submit(_fetch_store_products, m): m for m in merchants}
        for future in as_completed(futures):
            merchant = futures[future]
            try:
                products = future.result()
                all_products.extend(products)
            except Exception as e:
                logger.warning(f"[SHOPIFY] {merchant.name} fetch failed: {e}")

    if all_products:
        _all_products_cache = all_products
        print(f"[SHOPIFY] Total catalog: {len(_all_products_cache)} products across {len(merchants)} store(s)")
    else:
        print(f"[SHOPIFY] All stores failed -> falling back to mock catalog")
        from app.services import product_service
        _all_products_cache = product_service.get_all_products()

    return _all_products_cache


def invalidate_cache() -> None:
    global _all_products_cache
    _all_products_cache = None
    print("[SHOPIFY] Product cache cleared")


def search_products(queries: list[str], limit: int = 20) -> list[Product]:
    print(f"[SHOPIFY] Searching across all stores | queries: {queries} | limit: {limit}")
    all_products = _get_all_products()

    # score_map: product_id -> (cumulative_score, Product)
    score_map: dict[str, tuple[int, Product]] = {}

    for query in queries:
        if not query:
            continue
        tokens = [t for t in query.lower().split() if len(t) >= 2]
        if not tokens:
            continue
        matched_this_query = 0
        for p in all_products:
            hit = 0
            title_lower = p.title.lower()
            for token in tokens:
                if token in title_lower:
                    hit += 3
                if token in p.category:
                    hit += 3
                if any(token in tag for tag in p.tags):
                    hit += 2
                if any(token in s for s in p.style):
                    hit += 1
                if any(token in c for c in p.colors):
                    hit += 4
            if hit > 0:
                matched_this_query += 1
                prev = score_map.get(p.id, (0, p))
                score_map[p.id] = (prev[0] + hit, p)
        print(f"[SHOPIFY]   query '{query}' -> {matched_this_query} matches")

    results = [p for _, p in sorted(score_map.values(), key=lambda x: x[0], reverse=True)]
    print(f"[SHOPIFY] Total results: {len(results[:limit])} products from {len({p.merchant_name for p in results[:limit]})} store(s)")
    return results[:limit]


def get_product_by_id(product_id: str) -> Product | None:
    for p in _get_all_products():
        if p.id == product_id:
            return p
    return None


def get_all_products(limit: int = 20) -> list[Product]:
    return _get_all_products()[:limit]


def get_products_by_titles(titles: list[str]) -> list[Product]:
    """Fetch specific products by exact title match (case-insensitive). Preserves order."""
    all_products = _get_all_products()
    title_map = {p.title.lower(): p for p in all_products}
    result = []
    for title in titles:
        p = title_map.get(title.lower())
        if p:
            result.append(p)
        else:
            print(f"[SHOPIFY] get_products_by_titles: '{title}' not found in catalog")
    return result
