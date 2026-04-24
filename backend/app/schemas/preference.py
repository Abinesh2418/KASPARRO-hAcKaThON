from pydantic import BaseModel
from typing import Optional, List


class Preferences(BaseModel):
    style: List[str] = []
    colors: List[str] = []
    sizes: List[str] = []
    budget_max: Optional[int] = None
    budget_min: Optional[int] = None
    occasions: List[str] = []


class VisualSearchResponse(BaseModel):
    attributes: dict
    products: List  # List[Product] — avoids circular import; validated in route
