import json
import logging
from typing import AsyncGenerator
from openai import AsyncAzureOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_client() -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )


async def call_json_agent(system_prompt: str, user_content: str) -> dict:
    """Call an agent that returns strict JSON. Used for all intermediate pipeline agents."""
    agent_name = system_prompt[:40].strip().replace('\n', ' ')
    print(f"[LLM] Calling JSON agent | model: {settings.AZURE_OPENAI_MODEL} | prompt_hint: '{agent_name}...'")
    client = _get_client()
    try:
        response = await client.chat.completions.create(
            model=settings.AZURE_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=800,
        )
        raw = response.choices[0].message.content or "{}"
        result = json.loads(raw)
        print(f"[LLM] JSON agent response received | keys: {list(result.keys())}")
        return result
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in agent: {e}")
        print(f"[LLM] ERROR: JSON decode failed -> {e}")
        return {}
    except Exception as e:
        logger.error(f"LLM agent call failed: {e}")
        print(f"[LLM] ERROR: Agent call failed -> {e}")
        return {}


async def stream_final_response(
    system_prompt: str,
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    """Stream the user-facing final response."""
    print(f"[LLM] Starting stream | model: {settings.AZURE_OPENAI_MODEL} | messages in context: {len(messages)}")
    client = _get_client()
    try:
        stream = await client.chat.completions.create(
            model=settings.AZURE_OPENAI_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + messages,
            stream=True,
            temperature=0.75,
            max_tokens=300,
        )
        chunk_count = 0
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                chunk_count += 1
                yield delta.content
        print(f"[LLM] Stream complete | {chunk_count} chunks received")
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        print(f"[LLM] ERROR: Streaming failed -> {e}")
        yield "I'm having trouble right now. Please try again in a moment."
