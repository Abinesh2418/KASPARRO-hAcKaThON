from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# In-memory cart store keyed by username
_carts: dict[str, list[dict]] = {}


class CartItem(BaseModel):
    username: str
    product_id: str
    title: str
    price: float
    image: str
    size: Optional[str] = None
    quantity: int = 1


@router.get("/cart")
def get_cart(username: str):
    print(f"[CART] Get cart for: {username} | {len(_carts.get(username, []))} items")
    return {"items": _carts.get(username, [])}


@router.post("/cart")
def add_to_cart(item: CartItem):
    cart = _carts.setdefault(item.username, [])
    # If same product+size exists, increment quantity
    for existing in cart:
        if existing["product_id"] == item.product_id and existing.get("size") == item.size:
            existing["quantity"] += 1
            print(f"[CART] Quantity increased: {item.title} (qty: {existing['quantity']}) for {item.username}")
            return {"items": cart}
    cart.append(item.model_dump())
    print(f"[CART] Added: {item.title} for {item.username} | Cart total: {len(cart)} items")
    return {"items": cart}


@router.delete("/cart/{product_id}")
def remove_from_cart(product_id: str, username: str):
    cart = _carts.get(username, [])
    _carts[username] = [i for i in cart if i["product_id"] != product_id]
    print(f"[CART] Removed product {product_id} for {username}")
    return {"items": _carts[username]}


@router.delete("/cart")
def clear_cart(username: str):
    _carts[username] = []
    print(f"[CART] Cleared cart for {username}")
    return {"items": []}
