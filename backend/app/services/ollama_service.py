import base64
import json
import httpx
from app.core.config import settings

VISION_PROMPT = """Analyze this fashion item image and extract the following attributes. Respond ONLY with valid JSON, no other text.

{
  "style": ["list of style descriptors e.g. casual, formal, streetwear, minimal, bohemian"],
  "colors": ["primary colors in the item"],
  "silhouette": "overall shape e.g. fitted, oversized, flowy, structured",
  "category": "one of: tops, bottoms, dresses, outerwear, shoes, accessories",
  "material_guess": "likely fabric e.g. cotton, denim, silk, leather",
  "occasion": ["suitable occasions e.g. casual, work, evening, sport"],
  "description": "one sentence describing the item"
}"""

_MOCK_ATTRIBUTES = {
    "style": ["casual", "minimal"],
    "colors": ["white", "neutral"],
    "silhouette": "relaxed",
    "category": "tops",
    "material_guess": "cotton",
    "occasion": ["casual", "everyday"],
    "description": "A clean, minimalist casual top suitable for everyday wear.",
}


async def analyze_image(image_bytes: bytes) -> dict:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_VISION_MODEL,
                    "prompt": VISION_PROMPT,
                    "images": [b64],
                    "stream": False,
                },
            )
            response.raise_for_status()
            raw = response.json().get("response", "")
            start, end = raw.find("{"), raw.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
            return _MOCK_ATTRIBUTES
    except Exception:
        # Ollama offline or model not loaded — return mock so demo keeps working
        return _MOCK_ATTRIBUTES
