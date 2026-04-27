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
          ├── Azure OpenAI (cloud)          → gpt-4o  (6-agent pipeline + streaming)
          ├── Ollama (local/network)        → llama3.2-vision  (visual search)
          └── Shopify GraphQL API (cloud)   → live product catalog (fallback: mock)
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
| Product Data | Shopify Storefront GraphQL API (fallback: 20-item mock catalog) |
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
| Persistence | `localStorage` (chat history, up to 30 saved chats) |

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
│   │   │   ├── orchestrator_service.py   # 6-agent pipeline coordinator
│   │   │   ├── llm_service.py            # Azure OpenAI JSON agent + streaming wrapper
│   │   │   ├── azure_service.py          # Fallback streaming chat (no pipeline)
│   │   │   ├── ollama_service.py         # Vision image analysis
│   │   │   ├── shopify_service.py        # Shopify GraphQL product fetch + search
│   │   │   ├── product_service.py        # Mock catalog (20 items, Shopify fallback)
│   │   │   └── preference_service.py     # In-memory session + preference extraction
│   │   ├── schemas/
│   │   │   ├── chat.py                   # ChatRequest, ChatMessage
│   │   │   ├── product.py                # Product schema
│   │   │   └── preference.py             # Preferences schema
│   │   └── core/
│   │       ├── config.py                 # Settings via pydantic-settings
│   │       ├── middleware.py             # CORS, exception handlers
│   │       └── prompts/
│   │           ├── orchestrator.py       # ORCHESTRATOR_PROMPT, FINAL_RESPONSE_PROMPT
│   │           ├── intent_agent.py       # Intent classification + extraction
│   │           ├── search_agent.py       # Search query generation
│   │           ├── compare_agent.py      # Product scoring + ranking
│   │           ├── explain_agent.py      # Styling rationale generation
│   │           └── cart_agent.py         # Cart interaction handling
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
│   │   │   ├── ChatInterface.tsx        # Main chat shell
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
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

The core of Kasparo's recommendation engine is a 6-step pipeline executed on every chat request.

```
User Message
     │
     ▼
1. Intent Agent          — classifies intent, extracts budget / occasion / style / recipient
     │
     ▼
2. Search Agent          — generates primary + variant + fallback Shopify search queries
     │
     ▼
3. Shopify Fetch         — fetches live candidate products matching the queries
     │
     ▼
4. Compare & Rank Agent  — scores each product 0–100, filters below 35, returns top 3
     │
     ▼
5. Explain Agent         — generates stylist-quality rationale for each recommendation
     │
     ▼
6. Stream Response       — Azure OpenAI streams the conversational final answer token-by-token
```

### Intent Types

| Intent | Trigger |
|---|---|
| `greeting` | Pure greeting or closing |
| `general_chat` | Feedback, non-shopping questions |
| `cart_add` | "Add to cart", "yes please", named product |
| `single_product` | One specific item request |
| `routine_builder` | Complete outfit / head-to-toe |
| `gift_finder` | Shopping for someone else |
| `comparison` | Compare two or more products |

### Product Scoring (Compare & Rank Agent)

| Dimension | Weight | Full Score Criteria |
|---|---|---|
| Occasion fit | 30 pts | Product occasion matches user's stated occasion exactly |
| Style match | 25 pts | All user style keywords present in product tags/style |
| Budget fit | 25 pts | Price within stated budget range |
| Category match | 20 pts | Product category matches requested category |

**Minimum threshold:** Products scoring below 35/100 are excluded. If all candidates fail, the pipeline returns empty with an explanation rather than surfacing poor matches.

**Hard constraints:** Explicit color rejection, wrong size, or material rejection → instant score of 0.

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
  "messages": [
    { "role": "user", "content": "previous turn" },
    { "role": "assistant", "content": "previous reply" }
  ],
  "pre_searched_products": []
}
```

**SSE event stream:**
```
data: {"type": "session_id", "session_id": "uuid-here"}
data: {"type": "token", "content": "Great"}
data: {"type": "token", "content": " choice"}
data: {"type": "metadata", "preferences": {...}, "products": [...]}
data: {"type": "done"}
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

**Cart item schema:**
```json
{
  "product_id": "...",
  "title": "...",
  "price": 2499.0,
  "image": "https://...",
  "size": "M",
  "quantity": 1,
  "username": "..."
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
  id: string;
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

### SSE Events
```typescript
type SSEEvent =
  | { type: "session_id"; session_id: string }
  | { type: "token"; content: string }
  | { type: "metadata"; preferences: Preferences; products: Product[]; auto_cart_products?: string[] }
  | { type: "done" }
  | { type: "error"; message: string }
```

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
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_MODEL=gpt-4o

# Ollama (vision)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_VISION_MODEL=llama3.2-vision:latest

# Shopify
SHOPIFY_STORE_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_storefront_token

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### `frontend/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running with Docker

```bash
cp backend/.env.example backend/.env
# Add Azure OpenAI credentials and Shopify credentials

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
