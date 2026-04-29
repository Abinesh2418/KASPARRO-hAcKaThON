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
    TRADEOFF_AGENT_PROMPT,
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


async def _run_tradeoff_agent(ranked_products, intent: dict) -> dict:
    print(f"[TRADEOFF AGENT] Running... | {len(ranked_products)} products")
    products_summary = [
        {
            "product_id": p.id,
            "title": p.title,
            "price": p.price,
            "category": p.category,
            "style": p.style,
            "colors": p.colors,
            "tags": p.tags,
        }
        for p in ranked_products
    ]
    payload = json.dumps({"ranked_products": products_summary, "intent": intent})
    result = await llm_service.call_json_agent(TRADEOFF_AGENT_PROMPT, payload)
    scored = result.get("scored_products", [])
    panels = result.get("tradeoff_panels", [])
    print(f"[TRADEOFF AGENT] Done -> {len(scored)} scored products, {len(panels)} panels")
    return result


async def _stream_final_response(
    intent: dict,
    compare_result: dict,
    explain_result: dict,
    history: list[dict],
    force_recommend: bool = False,
    max_products: int = 3,
) -> AsyncGenerator[str, None]:
    explanations = {
        e["product_id"]: e["why_recommended"]
        for e in explain_result.get("explanations", [])
    }
    ranked = compare_result.get("ranked_products", [])

    # Strip scores — LLM seeing low scores causes it to say "couldn't find"
    top_products_clean = [
        {k: v for k, v in p.items() if k != "score"}
        for p in ranked[:max_products]
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

    # Group cart items by merchant_url
    merchant_groups: dict[str, list[dict]] = {}
    for item in cart_items:
        # Fall back to first configured merchant if item has no merchant_url
        merchant_url = item.get("merchant_url") or (settings.merchants[0].url if settings.merchants else "")
        if merchant_url not in merchant_groups:
            merchant_groups[merchant_url] = []
        merchant_groups[merchant_url].append(item)

    print(f"[CHECKOUT] Grouped into {len(merchant_groups)} merchant(s): {list(merchant_groups.keys())}")

    grand_total = sum(i["price"] * i.get("quantity", 1) for i in cart_items)
    total_items = sum(i.get("quantity", 1) for i in cart_items)

    checkouts = []
    for step, (merchant_url, items) in enumerate(merchant_groups.items(), 1):
        # Find merchant config for storefront token
        merchant_cfg = settings.get_merchant_by_url(merchant_url)
        merchant_name = items[0].get("merchant_name") or (merchant_cfg.name if merchant_cfg else merchant_url.split(".")[0].title())

        subtotal = sum(i["price"] * i.get("quantity", 1) for i in items)
        item_count = sum(i.get("quantity", 1) for i in items)

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
            for i in items
        ]

        # Build cart_lines for this merchant
        cart_lines = [
            {"merchandiseId": i["variant_id"], "quantity": i.get("quantity", 1)}
            for i in items
            if i.get("variant_id")
        ]
        print(f"[CHECKOUT] {merchant_name}: {len(cart_lines)}/{len(items)} items have variant IDs")

        # Call Shopify cartCreate for this merchant
        checkout_url = f"https://{merchant_url}/cart"
        if cart_lines and merchant_cfg and merchant_cfg.storefront_token:
            try:
                result = await shopify_service.shopify_cart_create(
                    merchant_url=merchant_url,
                    storefront_token=merchant_cfg.storefront_token,
                    cart_lines=cart_lines,
                )
                checkout_url = result["checkout_url"]
                print(f"[CHECKOUT] {merchant_name}: cartCreate OK -> {checkout_url[:80]}")
            except Exception as e:
                logger.warning(f"[CHECKOUT] {merchant_name}: cartCreate failed: {e} — using fallback URL")
        else:
            print(f"[CHECKOUT] {merchant_name}: no variant IDs or token — using fallback URL")

        checkouts.append({
            "step": step,
            "merchant_name": merchant_name,
            "merchant_url": merchant_url,
            "items": checkout_items,
            "item_count": item_count,
            "subtotal": subtotal,
            "checkout_url": checkout_url,
        })

    is_multi = len(checkouts) > 1

    # Stream user-facing message
    names = ", ".join(f"**{i['title']}**" for i in cart_items[:2])
    extra = f" +{len(cart_items) - 2} more" if len(cart_items) > 2 else ""
    if is_multi:
        merchant_names = " and ".join(c["merchant_name"] for c in checkouts)
        msg = f"Here's your cart — {names}{extra}. You'll checkout separately with {merchant_names}. Tap the buttons below!"
    else:
        msg = f"Here's your cart — {names}{extra}. Tap below to complete your purchase!"
    for char in msg:
        yield {"type": "token", "content": char}

    yield {
        "type": "metadata",
        "preferences": preferences,
        "products": [],
        "show_checkout_cta": True,
        "show_cart_summary": True,
        "is_multi_merchant": is_multi,
        "merchant_count": len(checkouts),
        "checkouts": checkouts,
        "grand_total": grand_total,
        "total_items": total_items,
        "currency": "USD",
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
                msg = f"You have {len(cart)} item(s) in your cart: {lines}. Total: ${total:,.0f}."
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

        # ── Cart remove intent ───────────────────────────────────────────────
        if intent_type == "cart_remove":
            cart = cart_service.get_cart(username) if username else []
            if not cart:
                msg = "Your cart is already empty."
            else:
                user_lower = user_message.lower()
                # Check for "clear all" / "remove everything" / "empty cart"
                clear_all_keywords = ["everything", "all", "clear", "empty", "all items", "all products"]
                is_clear_all = any(kw in user_lower for kw in clear_all_keywords)
                if is_clear_all:
                    count = len(cart)
                    cart_service.clear_cart(username)
                    msg = f"Done! All {count} item{'s' if count != 1 else ''} have been removed. Your cart is now empty. What would you like to find?"
                else:
                    # Fuzzy-match against cart titles to remove a specific item
                    removed = None
                    for item in cart:
                        title_words = [w for w in item["title"].lower().split() if len(w) > 2]
                        if any(w in user_lower for w in title_words):
                            cart_service.remove_item(username, item["product_id"])
                            removed = item
                            break
                    if removed:
                        remaining = cart_service.get_cart(username)
                        if remaining:
                            remain_names = ", ".join(f"**{i['title']}**" for i in remaining)
                            msg = f"The **{removed['title']}** has been removed. You now have {remain_names} left. Would you like to add anything else?"
                        else:
                            msg = f"The **{removed['title']}** has been removed. Your cart is now empty. What would you like to find?"
                    else:
                        msg = "I couldn't find that item in your cart. Would you like me to show what's in your cart?"
            print(f"[ORCHESTRATOR] Cart remove handled -> '{msg[:80]}'")
            for char in msg:
                yield {"type": "token", "content": char}
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

            # Ordinal position map — check user message directly
            _ORDINALS = {
                "first": 0, "1st": 0,
                "second": 1, "2nd": 1,
                "third": 2, "3rd": 2,
                "fourth": 3, "4th": 3,
                "fifth": 4, "5th": 4,
            }
            user_lower = user_message.lower()
            positional_indices = sorted({
                idx for word, idx in _ORDINALS.items() if word in user_lower
            })
            if "last" in user_lower:
                positional_indices = sorted(set(positional_indices) | {len(last_products) - 1})

            # Check for "add all / add everything"
            add_all_keywords = ["all", "everything", "every", "all of them", "all items", "all products", "the lot"]
            wants_all = any(kw in user_lower for kw in add_all_keywords)

            if positional_indices:
                all_to_add = [last_products[i] for i in positional_indices if i < len(last_products)]
                print(f"[ORCHESTRATOR] Positional add ({positional_indices}) -> {[p.title for p in all_to_add]}")
            elif wants_all:
                all_to_add = last_products
                print(f"[ORCHESTRATOR] Add all -> {[p.title for p in all_to_add]}")
            elif requested_items:
                def _matches(product, query: str) -> bool:
                    title = product.title.lower()
                    # Use words >3 chars to skip noise; require ≥60% to match
                    q_words = [w for w in query.lower().split() if len(w) > 3]
                    if not q_words:
                        return False
                    hits = sum(1 for w in q_words if w in title)
                    return hits / len(q_words) >= 0.6
                matched = [p for p in last_products if any(_matches(p, q) for q in requested_items)]
                all_to_add = matched if matched else last_products
                print(f"[ORCHESTRATOR] Requested: {requested_items} -> matched: {[p.title for p in all_to_add]}")
            else:
                all_to_add = last_products
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

            routine_queries = search_result.get("routine_queries")
            if routine_queries and isinstance(routine_queries, list):
                # routine_builder: flatten all step-queries
                queries = []
                for rq in routine_queries:
                    if isinstance(rq, str):
                        queries.append(rq)
                    elif isinstance(rq, dict):
                        queries.append(rq.get("query", ""))
                queries = [q for q in queries if q]
            else:
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

        # ── Step 5: Explain ──────────────────────────────────────────────────
        print(f"[ORCHESTRATOR] Step 5/6 -> Explain Agent")
        explain_result = await _run_explain_agent(compare_result, intent, raw_products[:6])

        # ── Step 6: Stream final response ────────────────────────────────────
        print(f"[ORCHESTRATOR] Step 6/6 -> Streaming Final Response")
        max_products_in_response = 4 if intent_type == "routine_builder" else 3
        full_response = ""
        async for token in _stream_final_response(intent, compare_result, explain_result, list(messages), force_recommend, max_products=max_products_in_response):
            full_response += token
            yield {"type": "token", "content": token}
        print(f"[ORCHESTRATOR] Final response streamed ({len(full_response)} chars)")

        # ── Step 7: Metadata ─────────────────────────────────────────────────
        updated_prefs = _merge_intent_into_preferences(intent, preferences)
        # Only show product cards when products genuinely scored above threshold.
        # force_recommend=True means nothing matched — AI says "not available", so no cards.
        # Routine builder returns 1 product per step (max 4 steps); single product returns up to 3.
        if force_recommend:
            products_to_return = []
        elif intent_type == "routine_builder":
            # Sort by skincare/outfit routine step order so cards match the AI text
            _ROUTINE_STEP_ORDER = [
                "cleanser", "face wash", "cleansing", "micellar",   # step 1
                "toner", "mist", "essence",                          # step 2
                "serum", "treatment", "ampoule", "vitamin c",        # step 3
                "moisturizer", "moisturiser", "cream", "lotion",     # step 4
                "sunscreen", "spf", "sunblock", "uv",               # step 5
                "mask", "pack", "scrub",                             # step 6
            ]
            def _routine_sort_key(p):
                combined = (p.title + " " + " ".join(p.tags)).lower()
                for i, kw in enumerate(_ROUTINE_STEP_ORDER):
                    if kw in combined:
                        return i
                return len(_ROUTINE_STEP_ORDER)
            products_to_return = sorted(ranked_products[:4], key=_routine_sort_key)
        else:
            products_to_return = ranked_products[:3]

        # Store exactly what is shown as cards so cart_add always matches what user sees
        preference_service.set_last_products(session_id, products_to_return if products_to_return else raw_products[:3])
        print(f"[ORCHESTRATOR] Pipeline complete | Returning {len(products_to_return)} products (force_recommend={force_recommend}) | Updated prefs: {updated_prefs}")

        metadata_event: dict = {
            "type": "metadata",
            "preferences": updated_prefs,
            "products": [p.model_dump() for p in products_to_return],
        }

        # Run tradeoff agent only for single-product comparison (not routines/outfits)
        if not force_recommend and products_to_return and intent_type == "single_product":
            try:
                tradeoff_result = await _run_tradeoff_agent(products_to_return[:3], intent)
                scored_products = tradeoff_result.get("scored_products", [])
                tradeoff_panels = tradeoff_result.get("tradeoff_panels", [])
                if scored_products:
                    metadata_event["scored_products"] = scored_products
                if tradeoff_panels:
                    metadata_event["tradeoff_panels"] = tradeoff_panels
                print(f"[ORCHESTRATOR] Tradeoff matrix attached: {len(scored_products)} scored, {len(tradeoff_panels)} panels")
            except Exception as te:
                logger.warning(f"[ORCHESTRATOR] Tradeoff agent failed (non-critical): {te}")

        yield metadata_event
        yield {"type": "done"}

    except Exception as e:
        logger.error(f"Orchestrator pipeline failed: {e} — falling back to azure_service")
        print(f"[ORCHESTRATOR] FAILED: {e} | Falling back to azure_service")
        async for event in azure_service.stream_chat(messages, preferences):
            yield event
        yield {"type": "metadata", "preferences": preferences, "products": []}
        yield {"type": "done"}
