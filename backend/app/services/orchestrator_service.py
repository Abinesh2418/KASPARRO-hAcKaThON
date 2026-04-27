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
    print(f"[INTENT AGENT] Running... | Message: '{user_message[:80]}{'...' if len(user_message) > 80 else ''}'")
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in history[-6:]
    )
    user_content = f"CONVERSATION HISTORY:\n{history_text}\n\nLATEST USER MESSAGE:\n{user_message}"
    result = await llm_service.call_json_agent(INTENT_AGENT_PROMPT, user_content)
    logger.info(f"Intent: {json.dumps(result)}")
    print(f"[INTENT AGENT] Result -> category: {result.get('product_category')} | budget: {result.get('budget_min')}-{result.get('budget_max')} | occasion: {result.get('occasion')} | needs_clarification: {result.get('needs_clarification')}")
    return result


async def _run_search_agent(intent: dict) -> dict:
    print(f"[SEARCH AGENT] Running... | Intent: {intent.get('product_category')} | preferences: {intent.get('preferences')}")
    result = await llm_service.call_json_agent(
        SEARCH_AGENT_PROMPT, json.dumps(intent)
    )
    logger.info(f"Search: {json.dumps(result)}")
    print(f"[SEARCH AGENT] Result -> primary_query: '{result.get('primary_query')}' | variants: {result.get('query_variants')} | budget_feasibility: {result.get('budget_feasibility')}")
    return result


async def _run_compare_agent(raw_products, intent: dict) -> dict:
    print(f"[COMPARE AGENT] Running... | Comparing {len(raw_products)} products against intent")
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
    ranked = result.get("ranked_products", [])
    top_summary = [f"{p.get('product_id')} (score:{p.get('score')})" for p in ranked[:3]]
    print(f"[COMPARE AGENT] Result -> {len(ranked)} ranked | Top: {top_summary} | needs_tiebreaker: {result.get('needs_tiebreaker')}")
    return result


async def _run_explain_agent(compare_result: dict, intent: dict, raw_products) -> dict:
    ranked = compare_result.get("ranked_products", [])
    print(f"[EXPLAIN AGENT] Running... | Explaining top {len(ranked)} ranked products")
    products_summary = [
        {"product_id": p.id, "title": p.title, "price": p.price, "description": p.description}
        for p in raw_products
    ]
    payload = json.dumps({
        "ranked_products": ranked,
        "intent": intent,
        "all_candidates": products_summary,
    })
    result = await llm_service.call_json_agent(EXPLAIN_AGENT_PROMPT, payload)
    logger.info(f"Explain: {json.dumps(result)}")
    explanations = result.get("explanations", [])
    for e in explanations:
        print(f"[EXPLAIN AGENT]   -> {e.get('product_id')}: {e.get('why_recommended', '')[:80]}")
    return result


async def _stream_final_response(
    intent: dict,
    compare_result: dict,
    explain_result: dict,
    history: list[dict],
    force_recommend: bool = False,
) -> AsyncGenerator[str, None]:
    explanations = {
        e["product_id"]: e["why_recommended"]
        for e in explain_result.get("explanations", [])
    }
    ranked = compare_result.get("ranked_products", [])

    # Strip scores — LLM seeing low scores causes it to say "couldn't find"
    top_products_clean = [
        {k: v for k, v in p.items() if k != "score"}
        for p in ranked[:3]
    ]

    force_note = (
        "\nINSTRUCTION: These are the BEST AVAILABLE products in the catalog. "
        "You MUST recommend them positively. NEVER say 'I couldn't find' when products are listed. "
        "If not a perfect match, say: 'The closest I found is [title] — [why it still works].'\n"
        if force_recommend else ""
    )

    context = (
        f"USER INTENT: {json.dumps(intent)}\n\n"
        f"TOP PRODUCTS: {json.dumps(top_products_clean)}\n\n"
        f"EXPLANATIONS: {json.dumps(explanations)}\n\n"
        f"TIEBREAKER NEEDED: {compare_result.get('needs_tiebreaker', False)}\n"
        f"TIEBREAKER QUESTION: {compare_result.get('tiebreaker_question')}\n"
        f"RELAXED CONSTRAINT: {compare_result.get('relaxed_constraint')}"
        f"{force_note}"
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
    pre_searched_products: list[dict] | None = None,
) -> AsyncGenerator[dict, None]:
    """
    Full multi-agent pipeline. Yields SSE-compatible dicts.
    Falls back to azure_service on any unrecoverable error.
    """
    user_message = messages[-1]["content"] if messages else ""
    history = messages[:-1]
    print(f"[ORCHESTRATOR] Pipeline started | session: {session_id} | history: {len(history)} msgs")

    try:
        # ── Step 1: Intent ───────────────────────────────────────────────────
        print(f"[ORCHESTRATOR] Step 1/6 -> Intent Agent")
        intent = await _run_intent_agent(user_message, history)

        if not intent:
            raise ValueError("Intent agent returned empty response")

        intent_type = intent.get("intent_type", "single_product")
        print(f"[ORCHESTRATOR] Intent type: {intent_type}")

        # ── Non-shopping: greeting or general chat ───────────────────────────
        if intent_type in ("greeting", "general_chat"):
            print(f"[ORCHESTRATOR] Non-shopping intent -> skipping product pipeline")
            async for event in azure_service.stream_chat(messages, preferences):
                yield event
            yield {"type": "metadata", "preferences": preferences, "products": []}
            yield {"type": "done"}
            return

        # ── Cart add intent ──────────────────────────────────────────────────
        if intent_type == "cart_add":
            print(f"[ORCHESTRATOR] Cart add intent -> fetching last recommended products")
            last_products = preference_service.get_last_products(session_id)
            if not last_products:
                msg = "I don't see any recent recommendations to add. What would you like to find?"
                print(f"[ORCHESTRATOR] No last products found for cart add")
                for char in msg:
                    yield {"type": "token", "content": char}
                yield {"type": "metadata", "preferences": preferences, "products": []}
                yield {"type": "done"}
                return

            # Match specific requested items if user named them
            requested_items = intent.get("requested_items", [])
            if requested_items:
                def _matches(product, query: str) -> bool:
                    title = product.title.lower()
                    return any(word in title for word in query.lower().split() if len(word) > 2)
                matched = [p for p in last_products if any(_matches(p, q) for q in requested_items)]
                all_to_add = matched if matched else last_products[:3]
                print(f"[ORCHESTRATOR] Requested: {requested_items} -> matched: {[p.title for p in all_to_add]}")
            else:
                all_to_add = last_products[:3]
                print(f"[ORCHESTRATOR] No specific items requested -> adding all: {[p.title for p in all_to_add]}")

            names = " + ".join(f"**{p.title}**" for p in all_to_add)
            msg = f"Adding {names} to your bag! Head to the Cart page to review your items."
            for char in msg:
                yield {"type": "token", "content": char}
            yield {
                "type": "metadata",
                "preferences": preferences,
                "products": [],
                "auto_cart_products": [p.model_dump() for p in all_to_add],
            }
            yield {"type": "done"}
            return

        # If agent needs clarification, stream the question and stop
        if intent.get("needs_clarification") and intent.get("clarification_question"):
            question = intent["clarification_question"]
            print(f"[ORCHESTRATOR] Needs clarification -> asking: '{question}'")
            for char in question:
                yield {"type": "token", "content": char}
            yield {"type": "metadata", "preferences": preferences, "products": []}
            yield {"type": "done"}
            return

        # ── Step 2 & 3: Search (or use pre-searched from visual search) ─────────
        if pre_searched_products:
            from app.schemas.product import Product
            print(f"[ORCHESTRATOR] Visual search products provided -> skipping search agents ({len(pre_searched_products)} products)")
            raw_products = [Product(**p) for p in pre_searched_products]
        else:
            print(f"[ORCHESTRATOR] Step 2/6 -> Search Agent")
            search_result = await _run_search_agent(intent)
            queries = [
                search_result.get("primary_query", ""),
                *search_result.get("query_variants", [])[:2],
            ]
            if search_result.get("fallback_query"):
                queries.append(search_result["fallback_query"])
            print(f"[ORCHESTRATOR] Search queries built: {queries}")

            print(f"[ORCHESTRATOR] Step 3/6 -> Shopify Product Search")
            raw_products = shopify_service.search_products(queries, limit=10)
        print(f"[ORCHESTRATOR] Products found: {len(raw_products)} | Titles: {[p.title for p in raw_products[:4]]}")
        if not raw_products:
            no_match_msg = (
                f"I couldn't find any products matching your request in our current catalog. "
                f"Could you try describing the style differently, or would you like to see what's available?"
            )
            print(f"[ORCHESTRATOR] No products found -> telling user")
            for char in no_match_msg:
                yield {"type": "token", "content": char}
            yield {"type": "metadata", "preferences": preferences, "products": []}
            yield {"type": "done"}
            return

        # ── Step 4: Compare & rank ───────────────────────────────────────────
        print(f"[ORCHESTRATOR] Step 4/6 -> Compare & Rank Agent")
        compare_result = await _run_compare_agent(raw_products, intent)

        ranked_ids = [
            p["product_id"]
            for p in compare_result.get("ranked_products", [])
            if p.get("score", 0) >= 35
        ]
        product_map = {p.id: p for p in raw_products}
        ranked_products = [product_map[pid] for pid in ranked_ids if pid in product_map]
        print(f"[ORCHESTRATOR] Ranked products (score>=35): {[p.title for p in ranked_products[:3]]}")

        force_recommend = False
        if not ranked_products:
            # All products scored too low — use best available and force positive recommendation
            force_recommend = True
            best = sorted(
                compare_result.get("ranked_products", []),
                key=lambda p: p.get("score", 0),
                reverse=True,
            )[:3]
            best_ids = [p["product_id"] for p in best]
            ranked_products = [product_map[pid] for pid in best_ids if pid in product_map]
            print(f"[ORCHESTRATOR] No products passed score threshold -> using best available (force_recommend=True): {[p.title for p in ranked_products]}")

        # Store for future cart_add intent
        products_to_store = ranked_products if ranked_products else raw_products[:3]
        preference_service.set_last_products(session_id, products_to_store)

        # ── Step 5: Explain ──────────────────────────────────────────────────
        print(f"[ORCHESTRATOR] Step 5/6 -> Explain Agent")
        explain_result = await _run_explain_agent(compare_result, intent, raw_products[:6])

        # ── Step 6: Stream final response ────────────────────────────────────
        print(f"[ORCHESTRATOR] Step 6/6 -> Streaming Final Response")
        full_response = ""
        async for token in _stream_final_response(intent, compare_result, explain_result, list(messages), force_recommend):
            full_response += token
            yield {"type": "token", "content": token}
        print(f"[ORCHESTRATOR] Final response streamed ({len(full_response)} chars)")

        # ── Step 7: Metadata ─────────────────────────────────────────────────
        updated_prefs = _merge_intent_into_preferences(intent, preferences)
        products_to_return = ranked_products[:6] if ranked_products else raw_products[:6]
        print(f"[ORCHESTRATOR] Pipeline complete | Returning {len(products_to_return)} products | Updated prefs: {updated_prefs}")

        yield {
            "type": "metadata",
            "preferences": updated_prefs,
            "products": [p.model_dump() for p in products_to_return],
        }
        yield {"type": "done"}

    except Exception as e:
        logger.error(f"Orchestrator pipeline failed: {e} — falling back to azure_service")
        print(f"[ORCHESTRATOR] FAILED: {e} | Falling back to azure_service")
        async for event in azure_service.stream_chat(messages, preferences):
            yield event
