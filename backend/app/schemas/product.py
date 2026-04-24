from pydantic import BaseModel
from typing import Optional, List


class Product(BaseModel):
    id: str
    title: str
    price: float
    compare_at_price: Optional[float] = None
    images: List[str]
    category: str
    colors: List[str]
    sizes: List[str]
    style: List[str]
    tags: List[str]
    description: str
    rating: float
    reviews_count: int
