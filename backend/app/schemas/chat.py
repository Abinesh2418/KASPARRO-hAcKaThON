from pydantic import BaseModel
from typing import Optional, List, Any


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    messages: List[ChatMessage] = []
    pre_searched_products: Optional[List[Any]] = None
