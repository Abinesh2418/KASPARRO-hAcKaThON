import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services import cart_service, shopify_service
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class CartItem(BaseModel):
    username: str
    product_id: str
    title: str
    price: float
    image: str
    size: Optional[str] = None
    quantity: int = 1
    variant_id: Optional[str] = None
    merchant_url: Optional[str] = None
    merchant_name: Optional[str] = None


@router.get("/cart")
def get_cart(username: str):
    items = cart_service.get_cart(username)
    print(f"[CART] Get cart for: {username} | {len(items)} items")
    return {"items": items}


@router.post("/cart")
def add_to_cart(item: CartItem):
    items = cart_service.add_item(item.username, item.model_dump())
    print(f"[CART] Added: {item.title} for {item.username} | Cart total: {len(items)} items")
    return {"items": items}


@router.delete("/cart/{product_id}")
def remove_from_cart(product_id: str, username: str):
    items = cart_service.remove_item(username, product_id)
    print(f"[CART] Removed product {product_id} for {username}")
    return {"items": items}


@router.delete("/cart")
def clear_cart(username: str):
    cart_service.clear_cart(username)
    print(f"[CART] Cleared cart for {username}")
    return {"items": []}


@router.get("/cart/checkout")
async def get_checkout_urls(username: str):
    """
    Group cart items by merchant and call Shopify cartCreate for each.
    Returns per-merchant checkout URLs ready to open in the browser.
    """
    cart_items = cart_service.get_cart(username)
    if not cart_items:
        return {"checkouts": [], "grand_total": 0, "total_items": 0}

    # Group by merchant_url
    merchant_groups: dict[str, list[dict]] = {}
    for item in cart_items:
        url = item.get("merchant_url") or (settings.merchants[0].url if settings.merchants else "")
        merchant_groups.setdefault(url, []).append(item)

    grand_total = sum(i["price"] * i.get("quantity", 1) for i in cart_items)
    total_items = sum(i.get("quantity", 1) for i in cart_items)

    checkouts = []
    for step, (merchant_url, items) in enumerate(merchant_groups.items(), 1):
        merchant_cfg = settings.get_merchant_by_url(merchant_url)
        merchant_name = items[0].get("merchant_name") or (merchant_cfg.name if merchant_cfg else merchant_url.split(".")[0].title())
        subtotal = sum(i["price"] * i.get("quantity", 1) for i in items)
        item_count = sum(i.get("quantity", 1) for i in items)

        cart_lines = [
            {"merchandiseId": i["variant_id"], "quantity": i.get("quantity", 1)}
            for i in items
            if i.get("variant_id")
        ]

        checkout_url = f"https://{merchant_url}/cart"
        if cart_lines and merchant_cfg and merchant_cfg.storefront_token:
            try:
                result = await shopify_service.shopify_cart_create(
                    merchant_url=merchant_url,
                    storefront_token=merchant_cfg.storefront_token,
                    cart_lines=cart_lines,
                )
                checkout_url = result["checkout_url"]
                print(f"[CART CHECKOUT] {merchant_name}: cartCreate OK")
            except Exception as e:
                logger.warning(f"[CART CHECKOUT] {merchant_name}: cartCreate failed: {e}")

        checkouts.append({
            "step": step,
            "merchant_name": merchant_name,
            "merchant_url": merchant_url,
            "checkout_url": checkout_url,
            "subtotal": subtotal,
            "item_count": item_count,
        })

    return {
        "checkouts": checkouts,
        "grand_total": grand_total,
        "total_items": total_items,
        "is_multi_merchant": len(checkouts) > 1,
    }
