"""
Centralized in-memory cart store.
Shared between the cart API router and the orchestrator (for checkout flow).
"""

_carts: dict[str, list[dict]] = {}


def get_cart(username: str) -> list[dict]:
    return list(_carts.get(username, []))


def add_item(username: str, item: dict) -> list[dict]:
    cart = _carts.setdefault(username, [])
    for existing in cart:
        if existing["product_id"] == item["product_id"] and existing.get("size") == item.get("size"):
            existing["quantity"] = existing.get("quantity", 1) + 1
            return list(cart)
    cart.append(item)
    return list(cart)


def remove_item(username: str, product_id: str) -> list[dict]:
    _carts[username] = [i for i in _carts.get(username, []) if i["product_id"] != product_id]
    return list(_carts[username])


def clear_cart(username: str) -> list[dict]:
    _carts[username] = []
    return []
