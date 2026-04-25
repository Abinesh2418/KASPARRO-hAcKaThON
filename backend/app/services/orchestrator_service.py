"""
Multi-agent orchestration pipeline.

Flow per user message:
  Intent Agent → Search Agent → Shopify Search → Compare Agent → Explain Agent → Final Response (streamed)

Each intermediate agent returns strict JSON.
The final response is streamed token-by-token to the frontend.
If any step fails, the pipeline degrades gracefully to the azure_service fallback.
"""
import json
import logging
from typing import AsyncGenerator

from app.services import llm_service, shopify_service, preference_service, azure_service
from app.core.prompts import (
    INTENT_AGENT_PROMPT,
    SEARCH_AGENT_PROMPT,
    COMPARE_AGENT_PROMPT,
    EXPLAIN_AGENT_PROMPT,
)
from app.core.prompts.orchestrator import FINAL_RESPONSE_PROMPT

logger = logging.getLogger(__name__)


# ── Agent callers ────────────────────────────────────────────────────────────

async def _run_intent_agent(user_message: str, history: list[dict]) -> dict:
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in history[-6:]
    )
    user_content = f"CONVERSATION HISTORY:\n{history_text}\n\nLATEST USER MESSAGE:\n{user_message}"
    result = await llm_service.call_json_agent(INTENT_AGENT_PROMPT, user_content)
    logger.info(f"Intent: {json.dumps(result)}")
    return result


async def _run_search_agent(intent: dict) -> dict:
    result = await llm_service.call_json_agent(
        SEARCH_AGENT_PROMPT, json.dumps(intent)
    )
    logger.info(f"Search: {json.dumps(result)}")
    return result


async def _run_compare_agent(raw_products, intent: dict) -> dict:
    products_summary = [
        {
            "product_id": p.id,
            "title": p.title,
            "price": p.price,
            "category": p.category,
            "style": p.style,
            "colors": p.colors,
            "tags": p.tags,
            "sizes": p.sizes,
        }
        for p in raw_products
    ]
    payload = json.dumps({"raw_products": products_summary, "intent": intent})
    result = await llm_service.call_json_agent(COMPARE_AGENT_PROMPT, payload)
    logger.info(f"Compare: {json.dumps(result)}")
    return result


async def _run_explain_agent(compare_result: dict, intent: dict, raw_products) -> dict:
    products_summary = [
        {"product_id": p.id, "title": p.title, "price": p.price, "description": p.description}
        for p in raw_products
    ]
    payload = json.dumps({
        "ranked_products": compare_result.get("ranked_products", []),
        "intent": intent,
        "all_candidates": products_summary,
    })
    result = await llm_service.call_json_agent(EXPLAIN_AGENT_PROMPT, payload)
    logger.info(f"Explain: {json.dumps(result)}")
    return result


async def _stream_final_response(
    intent: dict,
    compare_result: dict,
    explain_result: dict,
    history: list[dict],
) -> AsyncGenerator[str, None]:
    explanations = {
        e["product_id"]: e["why_recommended"]
        for e in explain_result.get("explanations", [])
    }
    ranked = compare_result.get("ranked_products", [])

    context = (
        f"USER INTENT: {json.dumps(intent)}\n\n"
        f"TOP PRODUCTS: {json.dumps(ranked[:3])}\n\n"
        f"EXPLANATIONS: {json.dumps(explanations)}\n\n"
        f"TIEBREAKER NEEDED: {compare_result.get('needs_tiebreaker', False)}\n"
        f"TIEBREAKER QUESTION: {compare_result.get('tiebreaker_question')}\n"
        f"RELAXED CONSTRAINT: {compare_result.get('relaxed_constraint')}"
    )

    messages = [
        *[{"role": m["role"], "content": m["content"]} for m in history[-4:]],
        {"role": "user", "content": context},
    ]

    async for token in llm_service.stream_final_response(FINAL_RESPONSE_PROMPT, messages):
        yield token


# ── Preference merge ─────────────────────────────────────────────────────────

def _merge_intent_into_preferences(intent: dict, existing: dict) -> dict:
    prefs = dict(existing)
    if intent.get("preferences"):
        prefs.setdefault("style", [])
        for p in intent["preferences"]:
            if p not in prefs["style"]:
                prefs["style"].append(p)
    if intent.get("budget_max"):
        prefs["budget_max"] = intent["budget_max"]
    if intent.get("occasion"):
        prefs.setdefault("occasions", [])
        if intent["occasion"] not in prefs["occasions"]:
            prefs["occasions"].append(intent["occasion"])
    return prefs


# ── Main pipeline ────────────────────────────────────────────────────────────

async def run_pipeline(
    messages: list[dict],
    preferences: dict,
    session_id: str,
) -> AsyncGenerator[dict, None]:
    """
    Full multi-agent pipeline. Yields SSE-compatible dicts.
    Falls back to azure_service on any unrecoverable error.
    """
    user_message = messages[-1]["content"] if messages else ""
    history = messages[:-1]

    try:
        # ── Step 1: Intent ───────────────────────────────────────────────────
        intent = await _run_intent_agent(user_message, history)

        if not intent:
            raise ValueError("Intent agent returned empty response")

        # If agent needs clarification, stream the question and stop
        if intent.get("needs_clarification") and intent.get("clarification_question"):
            question = intent["clarification_question"]
            for char in question:
                yield {"type": "token", "content": char}
            yield {"type": "metadata", "preferences": preferences, "products": []}
            yield {"type": "done"}
            return

        # ── Step 2: Search ───────────────────────────────────────────────────
        search_result = await _run_search_agent(intent)
        queries = [
            search_result.get("primary_query", ""),
            *search_result.get("query_variants", [])[:2],
        ]
        if search_result.get("fallback_query"):
            queries.append(search_result["fallback_query"])

        # ── Step 3: Get products ─────────────────────────────────────────────
        raw_products = shopify_service.search_products(queries, limit=10)
        if not raw_products:
            raw_products = shopify_service.get_all_products(limit=6)

        # ── Step 4: Compare & rank ───────────────────────────────────────────
        compare_result = await _run_compare_agent(raw_products, intent)

        ranked_ids = [
            p["product_id"]
            for p in compare_result.get("ranked_products", [])
        ]
        product_map = {p.id: p for p in raw_products}
        ranked_products = [product_map[pid] for pid in ranked_ids if pid in product_map]

        # ── Step 5: Explain ──────────────────────────────────────────────────
        explain_result = await _run_explain_agent(compare_result, intent, raw_products[:6])

        # ── Step 6: Stream final response ────────────────────────────────────
        full_response = ""
        async for token in _stream_final_response(intent, compare_result, explain_result, list(messages)):
            full_response += token
            yield {"type": "token", "content": token}

        # ── Step 7: Metadata ─────────────────────────────────────────────────
        updated_prefs = _merge_intent_into_preferences(intent, preferences)
        products_to_return = ranked_products[:6] if ranked_products else raw_products[:6]

        yield {
            "type": "metadata",
            "preferences": updated_prefs,
            "products": [p.model_dump() for p in products_to_return],
        }
        yield {"type": "done"}

    except Exception as e:
        logger.error(f"Orchestrator pipeline failed: {e} — falling back to azure_service")
        async for event in azure_service.stream_chat(messages, preferences):
            yield event
