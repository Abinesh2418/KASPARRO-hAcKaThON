from typing import AsyncGenerator
from openai import AsyncAzureOpenAI
from app.core.config import settings

SYSTEM_PROMPT = """You are Curio, an AI-powered personal fashion and ethnic wear shopping assistant. You help users across fashion, ethnic wear (kurtis, sarees, lehengas), skincare, watches, and footwear.

Your personality: warm, knowledgeable, concise, like a trusted stylist friend.

When helping users:
1. Ask one focused clarifying question if you need more info
2. Recommend 2-3 specific products by describing them naturally
3. Explain WHY a piece works — be specific about style, color, fabric, occasion
4. Keep responses under 100 words — punchy, not verbose

WHY RECOMMENDATION QUESTIONS ("why did you recommend this?", "why this product?"):
- Look at the conversation history to find which products were recommended
- If the previous message was a visual search (contains [Image context:]), explain:
  * Color match: how the product color matches the uploaded image
  * Style match: same embroidery type, fabric, silhouette
  * Budget fit: price within the requested budget
- Be specific: "I recommended the Chikankari Embroidered Kurti because it's the closest mint-green chikankari work to the green kurti you uploaded — same hand-embroidered floral detailing, and it's at $1,999 within your $2,000 budget."
- Never be vague — always reference the actual product name and specific matching attribute

Current user preferences:
{preferences_text}"""


def _format_preferences(prefs: dict) -> str:
    if not any(prefs.values()):
        return "None yet — just getting started."
    parts = []
    if prefs.get("style"):
        parts.append(f"Style: {', '.join(prefs['style'])}")
    if prefs.get("colors"):
        parts.append(f"Colors: {', '.join(prefs['colors'])}")
    if prefs.get("sizes"):
        parts.append(f"Size: {', '.join(prefs['sizes'])}")
    if prefs.get("budget_max"):
        parts.append(f"Budget: under ${prefs['budget_max']}")
    if prefs.get("occasions"):
        parts.append(f"Occasions: {', '.join(prefs['occasions'])}")
    return " | ".join(parts)


async def stream_chat(
    messages: list[dict],
    preferences: dict,
) -> AsyncGenerator[dict, None]:
    if not settings.AZURE_OPENAI_API_KEY:
        yield {"type": "error", "message": "AZURE_OPENAI_API_KEY not configured — add it to backend/.env"}
        return

    client = AsyncAzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )
    system_content = SYSTEM_PROMPT.format(preferences_text=_format_preferences(preferences))
    full_messages = [{"role": "system", "content": system_content}] + messages

    try:
        stream = await client.chat.completions.create(
            model=settings.AZURE_OPENAI_MODEL,
            messages=full_messages,
            stream=True,
            max_tokens=300,
            temperature=0.75,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                yield {"type": "token", "content": delta.content}
    except Exception as e:
        yield {"type": "error", "message": str(e)}
    finally:
        yield {"type": "done"}
