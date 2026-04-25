"""
Shopify service — currently backed by mock catalog.
Replace get_products() with Shopify Storefront API calls when credentials are available.
"""
import logging
from app.services import product_service
from app.schemas.product import Product

logger = logging.getLogger(__name__)


def search_products(queries: list[str], limit: int = 20) -> list[Product]:
    """
    Search products using multiple query terms.
    Merges results across all query variants, deduplicates by id.
    """
    all_products = product_service.get_all_products()
    results: list[Product] = []
    seen_ids: set[str] = set()

    for query in queries:
        if not query:
            continue
        q = query.lower()
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

    # Fallback: return all products if nothing matched
    if not results:
        logger.info("No keyword matches — returning full catalog as fallback")
        return all_products[:limit]

    return results[:limit]


def get_product_by_id(product_id: str) -> Product | None:
    for p in product_service.get_all_products():
        if p.id == product_id:
            return p
    return None


def get_all_products(limit: int = 20) -> list[Product]:
    return product_service.get_all_products()[:limit]
