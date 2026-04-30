# Decision Log — Curio AI Shopping Agent

Key architectural and product decisions made during the build, in "considered X, chose Y, because Z" format.

---

## 1. LLM Provider — Azure OpenAI over direct OpenAI API

Considered using the OpenAI API directly. Chose Azure OpenAI because it was the available hackathon resource and the endpoint/model are fully configurable via env vars, making it easy for judges to swap in their own credentials.

---

## 2. Vision Model — Ollama `llama3.2-vision` over Azure OpenAI Vision

Considered routing image analysis through Azure OpenAI's vision endpoint. Chose Ollama with `llama3.2-vision` because the model produces high-quality, detailed extraction of fashion-specific attributes from uploaded images — style, silhouette, color palette, category, and occasion — which is the core of the visual search feature. A richer attribute extraction directly improves the quality of product matches returned. The local deployment also keeps uploaded images off third-party APIs and avoids extra Azure token cost for image inputs.

---

## 3. Streaming Protocol — SSE over WebSockets

Considered WebSockets for the real-time chat stream. Chose Server-Sent Events because the communication is strictly server→client (tokens, agent steps, metadata). SSE is simpler to implement, works over plain HTTP without an upgrade handshake, and is natively consumable by `fetch` + `ReadableStream` on the frontend with no library.

---

## 4. Session Storage — In-memory dict over Redis/Postgres

Considered a proper persistence layer for session state (preferences, cart). Chose an in-memory Python dict because a hackathon demo doesn't require survival across server restarts, and eliminating a database dependency means zero infra setup for judges running it locally.

---

## 5. Multi-Agent Pipeline over a single large prompt

Considered one large system prompt that does intent extraction, ranking, explanation, and tradeoff analysis in a single LLM call. Chose a 7-step pipeline with dedicated agents because each agent can have its own focused prompt, failures are isolatable without losing the whole response, intermediate outputs can be streamed to the Live Agent Reasoning Panel, and the scoring logic (compare agent) runs in Python — not in the LLM — which is faster and deterministic.

---

## 6. Product Scoring Threshold — 35/100 hard cutoff

Considered soft ranking (always return top N regardless of score). Chose a hard exclusion threshold of 35/100 because early testing showed that without it, loosely-matching products surfaced frequently — a formal kurta appearing for "casual brunch" queries. The pipeline now returns an empty result with an explanation rather than a bad recommendation, which is a better user experience.

---

## 7. Preference Extraction — Regex over a dedicated LLM call

Considered calling the LLM again after each response to extract structured preferences (style, colors, sizes, budget). Chose regex + keyword matching against a fixed vocabulary (13 style terms, 18 colors, 10 occasions) because it runs synchronously in under 1ms, is deterministic, and the vocabulary is narrow enough that fuzzy matching isn't needed. Saves one round-trip per message.

---

## 8. Multi-Merchant Architecture — Parallel fan-out from day one

Considered starting with a single Shopify store and adding multi-merchant later. Built multi-merchant support from the start using numbered env vars (`_1`, `_2`, `_3`) and a `ThreadPoolExecutor` for parallel product fetch. This was the right call — the hackathon track explicitly expects multi-merchant, and retrofitting cart grouping and per-merchant `cartCreate` later would have required touching every layer.

---

## 9. Checkout URL Generation — Shopify `cartCreate` over deep-link URLs

Considered constructing simple Shopify cart URLs (`/cart/{variantId}:{qty}`) as a lightweight checkout path. Chose the Storefront API `cartCreate` mutation because it returns a real, pre-populated `checkoutUrl` that bypasses the cart page and takes the user directly to checkout — demonstrably better UX and a proper use of the Shopify Storefront API.

---

## 10. Frontend State — `useReducer` over Redux/Zustand

Considered a global state library. Chose `useReducer` inside `use-chat.ts` because the chat interface is a single, well-defined state machine (idle → streaming → complete → error) with no cross-component state sharing requirements. No library overhead, no boilerplate, and the reducer makes all state transitions auditable in one file.

---

## 11. Tradeoff Agent — Non-blocking, after main stream

Considered blocking the main recommendation stream until the tradeoff scores were ready. Chose to run the tradeoff agent after the conversational response completes and send its output as a separate SSE metadata event. Main recommendations arrive fast; the tradeoff matrix appears a moment later. Failure in the tradeoff step doesn't affect the primary response.

---

## 12. Tradeoff Dimensions — 7 over 3–5

Considered a simpler 3-score breakdown (fit, price, style). Chose 7 dimensions (occasion fit, style match, budget fit, category, color, availability, value) because each dimension maps to a real reason a shopper picks or rejects an item. The maximum of 135 also creates meaningful spread between products that would otherwise score similarly on just 3 axes.

---

## 13. Live Agent Reasoning Panel — Consumer-facing, not a dev log

Considered hiding the pipeline entirely behind a spinner. Chose to expose it as a consumer-facing feature because the pipeline takes 4–5 seconds and users need a reason to wait. The panel turns latency into a feature: seeing the AI think, search, fetch, score, and explain makes the recommendation feel earned rather than arbitrary.

---

## 14. Auth — File-based (`users.json`) over JWT + database

Considered a proper JWT authentication system with a user database. Chose a simple file-based store because the hackathon evaluation is on the shopping agent, not the auth layer. `users.json` is readable by judges without tooling, trivial to reset, and a 10-minute implementation instead of 2 hours.

---

## 15. Tradeoff Matrix — Single-product intent only

Considered running the tradeoff agent for all intent types including routine builder and comparison. Restricted to `single_product` (and similar focused intents) because a "build me an outfit" response may surface 6+ items across categories — comparing a kurta vs mojaris vs dupatta on the same 7 dimensions is meaningless. The tradeoff matrix is only useful when the top 3 are genuinely comparable alternatives.
