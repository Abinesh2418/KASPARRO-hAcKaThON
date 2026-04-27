from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services import cart_service

router = APIRouter()


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
