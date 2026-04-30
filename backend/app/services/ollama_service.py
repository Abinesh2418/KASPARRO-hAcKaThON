import base64
import json
import httpx
from app.core.config import settings

VISION_PROMPT = """Look at this image carefully and identify the main fashion or lifestyle product. Respond ONLY with valid JSON matching this exact structure, no other text.

CATEGORY DETECTION RULES (apply in order):
- If you see a KURTI / KURTA (Indian tunic top, usually knee-length or longer, worn by women, often with embroidery or prints) → category: "kurti"
- If you see a SAREE or LEHENGA (Indian draped garment or skirt-blouse set) → category: "saree" or "lehenga"
- If you see a SALWAR / CHURIDAR / PALAZZO (Indian lower garment worn with kurti) → category: "salwar"
- If you see an ETHNIC DRESS or ANARKALI (long flowy Indian dress) → category: "anarkali"
- If you see a WRISTWATCH / TIMEPIECE → category: "watch"
- If you see a WESTERN DRESS (non-Indian style) → category: "dress"
- If you see a SHIRT / TOP → category: "shirt"
- If you see JEANS / TROUSERS → category: "jeans"
- If you see SHOES / FOOTWEAR → category: "shoes"
- If you see a BAG / HANDBAG → category: "bag"

KEYWORD RULES:
- For kurti: always include "kurti" + fabric/embroidery type (chikankari, bandhani, block print, embroidered, printed) + neckline if visible (v-neck, round neck, mandarin collar)
- For watches: always include "watch" + style (analog, digital, smartwatch) + material (steel, leather)
- Be specific about Indian ethnic wear — mention chikankari, mirror work, phulkari, bandhani, ajrak if visible

{
  "keywords": ["3-5 most specific product search terms — e.g. for a chikankari kurti: 'kurti', 'chikankari kurti', 'embroidered kurti', 'v-neck kurti'"],
  "style": ["2-3 style words from: ethnic, bohemian, minimal, classic, casual, formal, festive, romantic, elegant, streetwear"],
  "colors": ["1-3 main colors visible — be specific: 'sage green', 'dusty rose', 'navy blue'"],
  "category": "ONE word from: kurti OR saree OR lehenga OR anarkali OR salwar OR watch OR dress OR shirt OR jeans OR shoes OR jacket OR bag OR jewelry",
  "occasion": ["1-2 occasions: casual, college, office, festive, wedding, party, everyday"],
  "description": "one sentence: what is this product exactly — mention fabric/embroidery if visible"
}"""

_MOCK_ATTRIBUTES = {
    "keywords": ["kurti", "ethnic wear", "embroidered kurti"],
    "style": ["ethnic", "casual"],
    "colors": ["multicolor"],
    "category": "kurti",
    "occasion": ["casual", "everyday"],
    "description": "An embroidered ethnic kurti.",
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
