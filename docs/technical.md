# Kasparo — Technical Documentation

## Architecture Overview

Kasparo is a full-stack web application split into two independently deployable services: a Python/FastAPI backend and a Next.js frontend.

```
Browser
  │
  ├── http://localhost:3000    → Next.js 16 Frontend (React 19, Tailwind CSS v4)
  │
  └── http://localhost:8000   → FastAPI Backend
          │
          ├── Azure OpenAI (cloud)          → gpt-4o  (agent pipeline + streaming)
          ├── Ollama (local/network)        → llama3.2-vision  (visual search)
          └── Shopify GraphQL API (cloud)   → Admin API (product fetch) + Storefront API (cartCreate)
```

---

## Tech Stack

### Backend

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.104 |
| Server | Uvicorn (ASGI) |
| LLM — Agents & Chat | Azure OpenAI `gpt-4o` |
| LLM — Vision | Ollama `llama3.2-vision:latest` (configurable) |
| Product Data | Shopify Admin GraphQL API — product fetch across all merchants |
| Cart Creation | Shopify Storefront API — `cartCreate` mutation, authenticated via `SHOPIFY_STOREFRONT_TOKEN` per merchant |
| Checkout URLs | Shopify Storefront API — `cartCreate` returns a live `checkoutUrl` per merchant |
| Streaming | Server-Sent Events via `StreamingResponse` |
| Validation | Pydantic v2 |
| Session Storage | In-memory dict (per-process) |
| Config | `pydantic-settings` + `.env` file |

### Frontend

| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| Runtime | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| UI Components | Radix UI primitives |
| Icons | Lucide React |
| Animations | Framer Motion |
| State | `useReducer` (no global store) |
| HTTP / SSE | Native `fetch` + `ReadableStream` |
| Persistence | `localStorage` (chat history) |
---

## Project Structure

```
kasparo/
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI app factory
│   │   ├── api/
│   │   │   ├── router.py                 # Route aggregation
│   │   │   └── v1/
│   │   │       ├── chat.py               # POST /api/v1/chat  (SSE streaming)
│   │   │       ├── visual_search.py      # POST /api/v1/visual-search
│   │   │       ├── products.py           # GET  /api/v1/products
│   │   │       ├── preferences.py        # GET  /api/v1/preferences/{session_id}
│   │   │       ├── auth.py               # POST /api/v1/auth/login
│   │   │       ├── cart.py               # GET/POST/DELETE /api/v1/cart
│   │   │       └── health.py             # GET  /health
│   │   ├── services/
│   │   │   ├── orchestrator_service.py   # Agent pipeline coordinator + checkout handler
│   │   │   ├── llm_service.py            # Azure OpenAI JSON agent + streaming wrapper
│   │   │   ├── azure_service.py          # Fallback streaming chat (no pipeline)
│   │   │   ├── ollama_service.py         # Vision image analysis
│   │   │   ├── shopify_service.py        # Shopify product fetch + cartCreate
│   │   │   ├── cart_service.py           # Centralized in-memory cart store
│   │   │   ├── product_service.py        # Mock catalog (20 items, Shopify fallback)
│   │   │   └── preference_service.py     # In-memory session + preference extraction
│   │   ├── schemas/
│   │   │   ├── chat.py                   # ChatRequest (prompt, session_id, username)
│   │   │   ├── product.py                # Product schema
│   │   │   └── preference.py             # Preferences schema
│   │   └── core/
│   │       ├── config.py                 # Settings via pydantic-settings
│   │       ├── middleware.py             # CORS, exception handlers
│   │       └── prompts/
│   │           ├── orchestrator.py       # ORCHESTRATOR_PROMPT, FINAL_RESPONSE_PROMPT
│   │           ├── intent_agent.py       # 11-intent classifier + entity extraction
│   │           ├── search_agent.py       # Search query generation
│   │           ├── compare_agent.py      # Product scoring + ranking (0–100, threshold 35)
│   │           ├── explain_agent.py      # Styling rationale generation
│   │           ├── tradeoff_agent.py     # Visual tradeoff scoring (0–135, 7 dimensions)
│   │           ├── cart_agent.py         # Cart add — variant picking, merchant grouping
│   │           └── checkout_agent.py     # Checkout — cart validation, cartCreate payload
│   ├── db/
│   │   └── users.json                    # User store (file-based auth)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                    # Root layout with sidebar
│   │   ├── page.tsx                      # Home page (hero + feature overview)
│   │   ├── login/page.tsx               # Login page
│   │   ├── curio/page.tsx               # Curio AI chat page
│   │   ├── cart/page.tsx                # Cart page
│   │   ├── profile/page.tsx             # Style profile page
│   │   └── globals.css
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx              # Left nav sidebar
│   │   │   └── ClientLayout.tsx         # Client-side layout wrapper
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx        # Main chat shell + Chats/Agents tab switcher
│   │   │   ├── AgentPanel.tsx           # Live 8-agent reasoning panel (idle/running/complete states)
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx        # Message + inline checkout card + tradeoff matrix
│   │   │   ├── TradeoffMatrix.tsx       # 7-dimension score table + Best Fit / Best Value panels
│   │   │   ├── ChatInput.tsx            # Text + image upload input
│   │   │   └── TypingIndicator.tsx
│   │   ├── products/
│   │   │   ├── ProductCard.tsx
│   │   │   └── InlineProducts.tsx       # Horizontal carousel in chat
│   │   ├── preferences/
│   │   │   └── PreferencePanel.tsx      # Live style profile panel
│   │   └── visual-search/
│   │       └── AttributeTags.tsx        # Extracted image attribute display
│   ├── hooks/
│   │   ├── use-chat.ts                  # Chat state machine (useReducer)
│   │   └── use-cart.ts                  # Cart state
│   ├── services/
│   │   └── api.ts                       # Fetch wrappers + SSE async generator
│   ├── types/
│   │   └── index.ts                     # All TypeScript interfaces
│   └── lib/
│       └── utils.ts
│
├── docs/
│   ├── ps.md                            # Hackathon problem statement
│   ├── product.md
│   └── technical.md
├── docker-compose.yml
└── README.md
```

---

## Multi-Agent Pipeline

### Shopping Pipeline (product discovery)

Runs on every shopping-related message. 7 steps.

```
User Message
     │
     ▼
1. Intent Agent          — classifies intent (11 types), extracts budget / occasion / style / recipient
     │
     ▼
2. Search Agent          — generates primary + variant + fallback Shopify search queries
     │
     ▼
3. Shopify Fetch         — fetches live candidate products across ALL configured stores in parallel
     │
     ▼
4. Compare & Rank Agent  — scores each product 0–100 across 4 dimensions, filters below 35, returns top 3
     │
     ▼
5. Explain Agent         — generates stylist-quality rationale for each recommendation
     │
     ▼
6. Stream Response       — Azure OpenAI streams the conversational final answer token-by-token
     │
     ▼
7. Tradeoff Agent        — scores top 3 products across 7 dimensions (0–135), generates Best Fit / Best Value panels (single_product only)
```

### Checkout Pipeline

Runs when intent is `checkout_request`.

```
User: "I'm done / checkout / ready to pay"
     │
     ▼
1. Checkout Agent        — validates cart, groups items by merchant, formats cart_lines
     │
     ▼
2. Shopify cartCreate    — calls Storefront API per merchant → gets real checkout URL
     │
     ▼
3. Stream Response       — streams cart summary message
     │
     ▼
4. Checkout Metadata     — sends inline cart card data + checkout URLs via SSE metadata event
```

### Intent Types

| Intent | Trigger |
|---|---|
| `greeting` | Pure greeting or closing |
| `general_chat` | Feedback, non-shopping questions |
| `cart_add` | "Add to cart", "yes please", "the first one in M" |
| `checkout_request` | "Checkout", "I'm done", "pay now", "bas itna hi" |
| `cart_view` | "What's in my cart?", "show me my cart" |
| `cart_remove` | "Remove the kurta", "take out the jeans" |
| `single_product` | One specific item request |
| `routine_builder` | Complete outfit / head-to-toe |
| `gift_finder` | Shopping for someone else |
| `comparison` | Compare two or more products |
| `style_refinement` | "Make it cheaper", "show me in navy", "more minimal" |

**Priority order:** `checkout_request` > `cart_remove` > `cart_view` > `cart_add` > all others

### Product Scoring (Compare & Rank Agent)

| Dimension | Weight | Full Score Criteria |
|---|---|---|
| Occasion fit | 30 pts | Product occasion matches user's stated occasion exactly |
| Style match | 25 pts | All user style keywords present in product tags/style |
| Budget fit | 25 pts | Price within stated budget range |
| Category match | 20 pts | Product category matches requested category |

**Minimum threshold:** Products scoring below 35/100 are excluded. If all candidates fail, the pipeline returns empty with an explanation rather than surfacing poor matches.

**Hard constraints:**
- Explicit color rejection, wrong size, or material rejection → instant score of 0
- Color preference filter: if user specifies a color (e.g. "silver"), non-matching products are capped at 25/135
- Formality mismatch: ethnic wear (kurti, kurta, salwar) scores 0 for formal/interview occasions
- Gender mismatch: women's products score 0 for men intent and vice versa

### Live Agent Reasoning Panel

A consumer-facing sidebar that visualises the 8-agent pipeline in real time. Implemented as a tab switcher (Chats | ✦ Agents) inside the left sidebar of the chat interface.

**SSE event:** The backend yields `agent_step` events interleaved with token events:
```json
{ "type": "agent_step", "agent": "compare", "status": "running" }
{ "type": "agent_step", "agent": "compare", "status": "complete", "data": { "total_candidates": 14, "finalists_count": 3, "ranked_products": [...] } }
```

**Agent step statuses:** `running` | `complete` | `skipped` | `waiting`

**Frontend state:**
- `agentSteps: AgentStep[]` — stored in `ChatState`, reset on every new user message via `RESET_PIPELINE` action
- `pipelineStartTime / pipelineEndTime` — used for the "Completed in X.Xs" footer
- Auto-switches sidebar to Agents tab when `agentSteps.length > 0`

**AgentPanel.tsx** — 8 cards rendered in canonical order:
- `waiting`: dashed border, 30% opacity
- `running`: violet glowing border, pulsing spinner
- `complete`: expanded content specific to each agent type
- `skipped`: single slim row, 40% opacity, no content

**Intent-aware pipeline events:**

| Intent type | Active agents | Skipped agents |
|---|---|---|
| shopping (single_product, gift_finder, etc.) | intent → search → fetch → compare → explain → tradeoff | cart, checkout |
| cart_add | intent, cart | search, fetch, compare, explain, tradeoff, checkout |
| checkout_request | intent, checkout | search, fetch, compare, explain, tradeoff, cart |
| needs_clarification | intent | all others |
| greeting / general_chat | none | panel stays idle |

**Key files:**
- `backend/app/services/orchestrator_service.py` — `_agent_step()` helper + yields throughout pipeline
- `frontend/components/chat/AgentPanel.tsx` — 8-card panel component with Framer Motion animations
- `frontend/hooks/use-chat.ts` — `RESET_PIPELINE`, `AGENT_STEP`, `PIPELINE_COMPLETE` reducer cases
- `frontend/types/index.ts` — `AgentName`, `AgentStatus`, `AgentStep`, `AgentStepData` types

### Visual Tradeoff Matrix (Tradeoff Agent)

Runs after the main pipeline for `single_product` intent only. Non-blocking — a failure does not affect the main recommendation.

Scores the top 3 ranked products across **7 dimensions** (max 135 total):

| Dimension | Max | Description |
|---|---|---|
| Occasion fit | 30 | How well it suits the stated occasion |
| Style match | 25 | Alignment with style preferences |
| Budget fit | 25 | Price vs. budget (25 = within, 0 = way over) |
| Category match | 20 | Correct product type |
| Color match | 15 | Color suitability for occasion/preference |
| Stock availability | 10 | Default 10 unless clearly limited |
| Value score | 10 | Price-to-quality ratio vs. other options |

Generates two tradeoff panels:
- **Best Value** — highest (value_score + budget_fit), with 12-word highlight and 10-word tradeoff
- **Best Fit** — highest (occasion_fit + style_match), same format

Quick-reply buttons: `Add to cart`, `Find cheaper options`, `Show similar styles`

The frontend renders this as an animated score bar table (emerald → amber → red gradient based on percentage) followed by the two panel cards with contextual add-to-cart labels.

### Fallback Behavior

If any pipeline step fails — LLM error, Shopify unavailable, parse error — the orchestrator degrades gracefully to a simple Azure OpenAI streaming chat response with current preference context injected.

---

## API Reference

### `POST /api/v1/chat`

Streams a shopping assistant response as Server-Sent Events.

**Request body:**
```json
{
  "prompt": "I need a casual outfit for a weekend brunch",
  "session_id": "abc123",
  "username": "abinesh",
  "messages": [
    { "role": "user", "content": "previous turn" },
    { "role": "assistant", "content": "previous reply" }
  ],
  "pre_searched_products": []
}
```

**SSE event stream (shopping):**
```
data: {"type": "session_id", "session_id": "uuid-here"}
data: {"type": "token", "content": "Great"}
data: {"type": "token", "content": " choice"}
data: {"type": "metadata", "preferences": {...}, "products": [...]}
data: {"type": "done"}
```

**SSE metadata event (checkout):**
```json
{
  "type": "metadata",
  "show_cart_summary": true,
  "show_checkout_cta": true,
  "is_multi_merchant": true,
  "merchant_count": 2,
  "checkouts": [
    {
      "step": 1,
      "merchant_name": "Veda",
      "merchant_url": "kasparro-curio-veda.myshopify.com",
      "items": [...],
      "subtotal": 1499.0,
      "item_count": 1,
      "checkout_url": "https://kasparro-curio-veda.myshopify.com/checkouts/cn/..."
    }
  ],
  "grand_total": 2798.0,
  "total_items": 2,
  "currency": "INR"
}
```

**Error event:**
```
data: {"type": "error", "message": "AZURE_OPENAI_API_KEY not configured"}
```

---

### `POST /api/v1/visual-search`

Analyzes an uploaded image and returns matched products.

**Request:** `multipart/form-data`, field `file` (JPEG / PNG / WEBP, max 5 MB)

**Response:**
```json
{
  "attributes": {
    "keywords": ["minimal", "casual"],
    "style": "casual",
    "colors": ["white", "navy"],
    "category": "tops",
    "occasion": "everyday",
    "description": "A clean minimal casual top"
  },
  "products": [ ...Product[] ]
}
```

---

### `GET /api/v1/products`

Returns products from the Shopify catalog (or mock fallback).

Query params: `category` (optional), `limit` (optional, default 20)

---

### `GET /api/v1/preferences/{session_id}`

Returns the current extracted preference state for a session.

**Response:**
```json
{
  "style": ["minimal", "casual"],
  "colors": ["navy", "white"],
  "occasions": ["office"],
  "sizes": ["M"],
  "budget_min": null,
  "budget_max": 5000
}
```

---

### `POST /api/v1/auth/login`

Authenticates a user against the file-based user store.

**Request:** `{ "username": "...", "password": "..." }`

**Response:** `{ "username": "...", "name": "..." }`

---

### `GET /api/v1/cart?username={username}`
### `POST /api/v1/cart`
### `DELETE /api/v1/cart/{product_id}?username={username}`

Cart read, add, and remove operations. Cart items are scoped to the logged-in user.

---

### `GET /api/v1/cart/checkout?username={username}`

Groups cart items by merchant, calls Shopify `cartCreate` for each store, and returns per-merchant checkout URLs.

**Response:**
```json
{
  "checkouts": [
    {
      "step": 1,
      "merchant_name": "Nova",
      "merchant_url": "kasparro-curio-nova.myshopify.com",
      "checkout_url": "https://kasparro-curio-nova.myshopify.com/checkouts/cn/...",
      "subtotal": 1499.0,
      "item_count": 1
    },
    {
      "step": 2,
      "merchant_name": "Indie",
      "merchant_url": "kasparro-curio-indie.myshopify.com",
      "checkout_url": "https://kasparro-curio-indie.myshopify.com/checkouts/cn/...",
      "subtotal": 1299.0,
      "item_count": 1
    }
  ],
  "grand_total": 2798.0,
  "total_items": 2,
  "is_multi_merchant": true
}
```

**Cart item schema:**
```json
{
  "product_id": "...",
  "title": "...",
  "price": 2499.0,
  "image": "https://...",
  "size": "M",
  "quantity": 1,
  "username": "...",
  "variant_id": "gid://shopify/ProductVariant/45111111",
  "merchant_url": "kasparro-curio-veda.myshopify.com",
  "merchant_name": "Veda"
}
```

---

### `GET /health`

```json
{
  "status": "ok",
  "azure": "configured",
  "ollama": "online"
}
```

---

## Data Models

### Product
```typescript
interface Product {
  id: string;            // "{merchant_slug}_{shopify_numeric_id}" — unique across stores
  title: string;
  price: number;
  compare_at_price?: number;
  images: string[];
  category: string;
  colors: string[];
  sizes: string[];
  style: string[];
  tags: string[];
  description: string;
  rating: number;
  reviews_count: number;
  variant_id?: string;   // default variant GID for cartCreate
  variants?: Array<{ id: string; size: string | null; price: number }>;
  merchant_name?: string; // e.g. "Nova", "Indie", "Kasparro"
  merchant_url?: string;  // e.g. "kasparro-curio-nova.myshopify.com"
}
```

### Preferences
```typescript
interface Preferences {
  style: string[];
  colors: string[];
  occasions: string[];
  sizes: string[];
  budget_min: number | null;
  budget_max: number | null;
}
```

### MerchantCheckout
```typescript
interface MerchantCheckout {
  step: number;
  merchant_name: string;
  merchant_url: string;
  cart_lines: Array<{ merchandiseId: string; quantity: number }>;
  items: CheckoutLineItem[];
  subtotal: number;
  item_count: number;
  checkout_url: string | null;
}
```

### SSE Events
```typescript
type SSEEvent =
  | { type: "session_id"; session_id: string }
  | { type: "token"; content: string }
  | { type: "metadata"; preferences: Preferences; products: Product[]; auto_cart_products?: Product[];
      // checkout fields (present when intent = checkout_request)
      show_cart_summary?: boolean; show_checkout_cta?: boolean;
      is_multi_merchant?: boolean; merchant_count?: number;
      checkouts?: MerchantCheckout[]; grand_total?: number;
      total_items?: number; currency?: string; }
  | { type: "done" }
  | { type: "error"; message: string }
```

---

## Shopify Integration — Multi-Merchant

### Configuration

Up to 3 Shopify stores are supported. Each store needs three credentials in `.env`:

```
SHOPIFY_STORE_URL_N      # domain only: kasparro-curio-nova.myshopify.com
SHOPIFY_ACCESS_TOKEN_N   # Admin API token (shpat_...) — product fetch
SHOPIFY_STOREFRONT_TOKEN_N  # Storefront API token — cart/checkout
SHOPIFY_MERCHANT_NAME_N  # display name: Nova, Indie, Kasparro
```

### Product Fetch (Admin API — parallel fan-out)

On first request, `shopify_service` fetches products from **all configured stores simultaneously** using `ThreadPoolExecutor`. Results are merged into a single in-process catalog cache. Each product is tagged with `merchant_name` and `merchant_url`.

Product IDs are namespaced as `{merchant_slug}_{shopify_numeric_id}` (e.g. `nova_8123456`) to guarantee uniqueness across stores.

Falls back to the 20-item mock catalog only if **all** stores fail.

### Checkout (Storefront API — per-merchant cartCreate)

When a user triggers checkout, cart items are grouped by `merchant_url`. For each merchant group, the backend calls Shopify's Storefront `cartCreate` mutation separately using that merchant's storefront token.

```graphql
mutation cartCreate($input: CartInput!) {
  cartCreate(input: $input) {
    cart {
      id
      checkoutUrl
      cost { totalAmount { amount currencyCode } }
    }
  }
}
```

The result is an array of merchant checkouts, each with its own `checkout_url`. The frontend displays one checkout button per merchant.

If `cartCreate` fails for any store, the backend falls back to a direct store cart URL (`https://{merchant_url}/cart`).

### Multi-Merchant Cart UX

- Product cards show a **merchant badge** (e.g. "Nova") below the title
- When products from multiple stores are added, the cart page groups items under merchant section headers
- Each merchant section has its own **Checkout** button that opens the real Shopify checkout in a new tab
- A multi-store info banner warns the user that separate checkouts are required
- The Curio chat checkout flow (saying "checkout" or "I'm done") also creates per-merchant checkout buttons inline in the conversation

---

## Streaming Implementation

The frontend consumes SSE via native `fetch` + `ReadableStream`:

```typescript
const res = await fetch(`${API_BASE}/api/v1/chat`, { method: "POST", body: ... });
const reader = res.body!.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n");
  buffer = lines.pop() ?? "";
  for (const line of lines) {
    if (line.startsWith("data: ")) {
      const event = JSON.parse(line.slice(6));
      // dispatch to useReducer
    }
  }
}
```

---

## Preference Extraction

Extracted synchronously after each assistant response using regex + keyword matching — no extra LLM call required.

| Field | Method |
|---|---|
| `style` | Matched against 13 style keywords |
| `colors` | Matched against 18 color keywords |
| `occasions` | Matched against 10 occasion keywords |
| `sizes` | Regex: `\b(xs\|s\|m\|l\|xl\|xxl\|\d{2})\b` |
| `budget_max` | Regex: `(under\|below\|max)\s*[$₹]?(\d+)` |

---

## Environment Variables

### `backend/.env`

```env
# ── Azure OpenAI ──────────────────────────────────────────────────────────────
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_MODEL=gpt-4o

# ── Ollama (vision model) ──────────────────────────────────────────────────────
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_VISION_MODEL=llama3.2-vision:latest

# ── Multi-Merchant Shopify Configuration ──────────────────────────────────────
# Each store requires 4 variables: STORE_URL, ACCESS_TOKEN (Admin API), STOREFRONT_TOKEN, MERCHANT_NAME
# STORE_URL        — domain only, e.g. your-store.myshopify.com
# ACCESS_TOKEN     — shpat_... Admin API token → used for product fetch (GraphQL Admin API)
# STOREFRONT_TOKEN — public storefront token → used for cartCreate / checkout (Storefront API)
# MERCHANT_NAME    — display name shown in product badges and checkout buttons

# Shopify Store 1 (e.g. Nova)
SHOPIFY_STORE_URL_1=your-store-1.myshopify.com
SHOPIFY_ACCESS_TOKEN_1=shpat_your_admin_api_token_1
SHOPIFY_STOREFRONT_TOKEN_1=your_storefront_token_1
SHOPIFY_MERCHANT_NAME_1=Nova

# Shopify Store 2 (e.g. Indie)
SHOPIFY_STORE_URL_2=your-store-2.myshopify.com
SHOPIFY_ACCESS_TOKEN_2=shpat_your_admin_api_token_2
SHOPIFY_STOREFRONT_TOKEN_2=your_storefront_token_2
SHOPIFY_MERCHANT_NAME_2=Indie

# Shopify Store 3 (optional — leave SHOPIFY_STORE_URL_3 blank to disable)
SHOPIFY_STORE_URL_3=
SHOPIFY_ACCESS_TOKEN_3=
SHOPIFY_STOREFRONT_TOKEN_3=
SHOPIFY_MERCHANT_NAME_3=

# ── Server ────────────────────────────────────────────────────────────────────
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

**Variable reference:**

| Variable | Required | Purpose |
|---|---|---|
| `AZURE_OPENAI_API_KEY` | Yes | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI resource endpoint URL |
| `AZURE_OPENAI_API_VERSION` | Yes | API version (e.g. `2024-12-01-preview`) |
| `AZURE_OPENAI_MODEL` | Yes | Deployment name (e.g. `gpt-4o`) |
| `OLLAMA_BASE_URL` | Yes | Ollama server URL (use `host.docker.internal:11434` in Docker) |
| `OLLAMA_VISION_MODEL` | Yes | Vision model name (e.g. `llama3.2-vision:latest`) |
| `SHOPIFY_STORE_URL_N` | Yes (≥1) | Shopify store domain — `your-store.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN_N` | Yes (≥1) | Admin API token (`shpat_...`) — used for product fetch |
| `SHOPIFY_STOREFRONT_TOKEN_N` | Yes (≥1) | Storefront API token — used for `cartCreate` and checkout URLs |
| `SHOPIFY_MERCHANT_NAME_N` | Yes (≥1) | Display name shown in product cards and checkout buttons |
| `HOST` | No | Server bind host (default `0.0.0.0`) |
| `PORT` | No | Server port (default `8000`) |
| `DEBUG` | No | Enable FastAPI debug mode (default `True`) |

At least one store (`_1`) must be configured. Stores `_2` and `_3` are optional — any store with a blank `SHOPIFY_STORE_URL_N` is skipped automatically.

### `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running with Docker

```bash
cp backend/.env.example backend/.env
# Add Azure OpenAI credentials and both Shopify tokens

docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py

# Frontend
cd frontend
npm install
npm run dev
```
