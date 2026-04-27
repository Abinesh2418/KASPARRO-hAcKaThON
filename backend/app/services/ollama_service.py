import base64
import json
import httpx
from app.core.config import settings

VISION_PROMPT = """Look at this image carefully and identify the main product. Respond ONLY with valid JSON matching this exact structure, no other text.

IMPORTANT: If you see a watch (wristwatch, timepiece, analog watch, digital watch), set category to "watch" and include "watch" and "analog" in keywords.

{
  "keywords": ["the 3-5 most specific product search terms — for a watch use: 'watch', 'analog watch', 'silver watch'; for a shirt use: 'shirt', 'formal shirt'; etc."],
  "style": ["2-3 style words: minimal, classic, casual, formal, sporty, elegant, streetwear"],
  "colors": ["1-3 main colors visible"],
  "category": "ONE word: watch OR dress OR shirt OR jeans OR shoes OR jacket OR bag OR jewelry",
  "occasion": ["1-2 occasions: casual, formal, office, sport, evening"],
  "description": "one sentence: what is this product exactly"
}"""

_MOCK_ATTRIBUTES = {
    "keywords": [],
    "style": ["casual", "minimal"],
    "colors": ["silver"],
    "category": "accessories",
    "occasion": ["casual", "everyday"],
    "description": "A product item.",
}


async def analyze_image(image_bytes: bytes) -> dict:
    print(f"[OLLAMA] Analyzing image | size: {len(image_bytes)/1024:.1f} KB | model: {settings.OLLAMA_VISION_MODEL} | url: {settings.OLLAMA_BASE_URL}")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            print(f"[OLLAMA] Sending image to Ollama vision model...")
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": settings.OLLAMA_VISION_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": VISION_PROMPT,
                            "images": [b64],
                        }
                    ],
                    "stream": False,
                    "keep_alive": "30m",
                },
            )
            response.raise_for_status()
            raw = response.json().get("message", {}).get("content", "")
            print(f"[OLLAMA] Raw response received ({len(raw)} chars)")
            start, end = raw.find("{"), raw.rfind("}") + 1
            if start >= 0 and end > start:
                result = json.loads(raw[start:end])
                print(f"[OLLAMA] Attributes extracted -> style: {result.get('style')} | colors: {result.get('colors')} | category: {result.get('category')}")
                return result
            print(f"[OLLAMA] No valid JSON in response -> using mock attributes")
            return _MOCK_ATTRIBUTES
    except Exception as e:
        print(f"[OLLAMA] FAILED ({e}) -> using mock attributes as fallback")
        return _MOCK_ATTRIBUTES
