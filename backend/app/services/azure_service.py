from typing import AsyncGenerator
from openai import AsyncAzureOpenAI
from app.core.config import settings

SYSTEM_PROMPT = """You are Curio, an AI-powered personal fashion shopping assistant for a premium e-commerce platform. You help users discover clothing and accessories they'll love through natural, engaging conversation.

Your personality: warm, knowledgeable about fashion trends, concise, and enthusiastic.

When helping users:
1. Ask one focused clarifying question if you need more info (style, occasion, budget, size)
2. Recommend 2-3 specific products by describing them naturally in your response
3. Explain WHY a piece works for their vibe or occasion
4. Keep responses under 120 words — be punchy, not verbose

Product categories available: tops, bottoms, dresses, outerwear, shoes, accessories

Current user preferences (learned from conversation):
{preferences_text}

If no preferences yet, ask a quick question to understand their style."""


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
