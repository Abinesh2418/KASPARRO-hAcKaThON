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

from app.services import llm_service, shopify_service, preference_service, azure_service, cart_service
from app.core.config import settings
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
        "\nINSTRUCTION: Nothing in the catalog genuinely matches what the user asked for. "
        "Do NOT recommend any of the products listed above — they do not fit. "
        "Tell the user clearly we don't carry that type right now. "
        "Suggest 1-2 alternative categories we DO have (e.g. kurtas, casual dresses, blazers, jeans) "
        "and ask if they'd like to explore those instead.\n"
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


# ── Checkout handler ─────────────────────────────────────────────────────────

async def _handle_checkout(
    user_message: str,
    username: str | None,
    preferences: dict,
    history: list[dict],
) -> AsyncGenerator[dict, None]:
    cart_items = cart_service.get_cart(username) if username else []
    print(f"[CHECKOUT] Running for user={username} | {len(cart_items)} cart items")

    if not cart_items:
        msg = "Your cart is empty. What would you like to find?"
        for char in msg:
            yield {"type": "token", "content": char}
        yield {"type": "metadata", "preferences": preferences, "products": []}
        yield {"type": "done"}
        return

    # Build cart_lines from stored variant_ids (set when products were added to cart)
    cart_lines = []
    for item in cart_items:
        vid = item.get("variant_id")
        if vid:
            cart_lines.append({"merchandiseId": vid, "quantity": item.get("quantity", 1)})
    print(f"[CHECKOUT] cart_lines with variant IDs: {len(cart_lines)} / {len(cart_items)} items")

    # Compute totals
    grand_total = sum(i["price"] * i.get("quantity", 1) for i in cart_items)
    total_items = sum(i.get("quantity", 1) for i in cart_items)
    merchant_url = settings.SHOPIFY_STORE_URL
    merchant_name = merchant_url.split(".")[0].replace("-", " ").title()

    # Build item details for the checkout card
    checkout_items = [
        {
            "title": i["title"],
            "size": i.get("size"),
            "color": None,
            "quantity": i.get("quantity", 1),
            "price": i["price"],
            "image": i.get("image", ""),
            "subtotal_for_line": i["price"] * i.get("quantity", 1),
        }
        for i in cart_items
    ]

    # Call Shopify cartCreate with real variant IDs
    checkout_url = f"https://{merchant_url}/cart"
    if cart_lines and settings.SHOPIFY_STOREFRONT_TOKEN:
        try:
            result = await shopify_service.shopify_cart_create(
                merchant_url=merchant_url,
                storefront_token=settings.SHOPIFY_STOREFRONT_TOKEN,
                cart_lines=cart_lines,
            )
            checkout_url = result["checkout_url"]
            print(f"[CHECKOUT] cartCreate OK: {checkout_url[:80]}")
        except Exception as e:
            logger.warning(f"[CHECKOUT] cartCreate failed: {e} — using fallback URL")
    else:
        print(f"[CHECKOUT] No variant_ids found — using store fallback URL")

    # Stream user-facing message
    names = ", ".join(f"**{i['title']}**" for i in cart_items[:2])
    extra = f" +{len(cart_items) - 2} more" if len(cart_items) > 2 else ""
    msg = f"Here's your cart — {names}{extra}. Tap below to complete your purchase!"
    for char in msg:
        yield {"type": "token", "content": char}

    checkouts = [{
        "merchant_name": merchant_name,
        "merchant_url": merchant_url,
        "items": checkout_items,
        "item_count": total_items,
        "subtotal": grand_total,
        "checkout_url": checkout_url,
        "step": 1,
    }]

    yield {
        "type": "metadata",
        "preferences": preferences,
        "products": [],
        "show_checkout_cta": True,
        "show_cart_summary": True,
        "is_multi_merchant": False,
        "merchant_count": 1,
        "checkouts": checkouts,
        "grand_total": grand_total,
        "total_items": total_items,
        "currency": "INR",
    }
    yield {"type": "done"}


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
    username: str | None = None,
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

        intent_type = intent.get("intent_type") or intent.get("intent", "single_product")
        print(f"[ORCHESTRATOR] Intent type: {intent_type}")

        # ── Checkout ─────────────────────────────────────────────────────────
        if intent_type == "checkout_request":
            print(f"[ORCHESTRATOR] Checkout intent -> running checkout agent")
            async for event in _handle_checkout(user_message, username, preferences, history):
                yield event
            return

        # ── Cart view ─────────────────────────────────────────────────────────
        if intent_type == "cart_view":
            cart = cart_service.get_cart(username) if username else []
            if not cart:
                msg = "Your cart is empty. What would you like to find?"
            else:
                lines = ", ".join(f"**{i['title']}**{' ('+i['size']+')' if i.get('size') else ''}" for i in cart)
                total = sum(i["price"] * i.get("quantity", 1) for i in cart)
                msg = f"You have {len(cart)} item(s) in your cart: {lines}. Total: ₹{total:,.0f}."
            for char in msg:
                yield {"type": "token", "content": char}
            yield {"type": "metadata", "preferences": preferences, "products": []}
            yield {"type": "done"}
            return

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
        # Only show product cards when products genuinely scored above threshold.
        # force_recommend=True means nothing matched — AI says "not available", so no cards.
        products_to_return = ranked_products[:6] if not force_recommend else []
        print(f"[ORCHESTRATOR] Pipeline complete | Returning {len(products_to_return)} products (force_recommend={force_recommend}) | Updated prefs: {updated_prefs}")

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
