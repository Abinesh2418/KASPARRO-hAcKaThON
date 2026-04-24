# Kasparo — Technical Documentation

## Architecture Overview

Kasparo is a full-stack web application split into two independently deployable services: a Python/FastAPI backend and a Next.js frontend. The backend orchestrates two LLMs — Azure OpenAI (GPT-4o) for conversational reasoning and Ollama (local) for multimodal image analysis.

```
Browser
  │
  ├── GET/POST http://localhost:3000     → Next.js Frontend (React, Tailwind)
  │
  └── POST/GET http://localhost:8000    → FastAPI Backend
          │
          ├── Azure OpenAI (cloud)      → gpt-4o (streaming chat)
          └── Ollama (local network)    → gemma4:26b (visual search)
```

---

## Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn (ASGI) |
| LLM — Chat | Azure OpenAI (`gpt-4o`) |
| LLM — Vision | Ollama (`gemma4:26b`) at `http://100.127.36.42:11434` |
| Streaming | Server-Sent Events (SSE) via `StreamingResponse` |
| Validation | Pydantic v2 |
| Session storage | In-memory dict |
| Config | `pydantic-settings` + `.env` file |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Next.js (App Router) |
| Runtime | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Components | Radix UI primitives |
| Icons | Lucide React |
| Animations | Framer Motion |
| State | `useReducer` (no global store) |
| HTTP | native `fetch` with `ReadableStream` for SSE |

---

## Project Structure

```
kasparo/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── chat.py               # POST /api/v1/chat (SSE streaming)
│   │   │   ├── products.py           # GET /api/v1/products
│   │   │   ├── visual_search.py      # POST /api/v1/visual-search
│   │   │   ├── preferences.py        # GET /api/v1/preferences/{session_id}
│   │   │   └── health.py             # GET /health
│   │   ├── services/
│   │   │   ├── azure_service.py      # Azure OpenAI streaming chat
│   │   │   ├── ollama_service.py     # Gemma4 visual analysis
│   │   │   ├── product_service.py    # Mock catalog + keyword matching
│   │   │   └── preference_service.py # Session state + preference extraction
│   │   ├── schemas/                  # Pydantic request/response models
│   │   └── core/                     # config.py, middleware.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                # Root layout with Sidebar
│   │   ├── page.tsx                  # Home page (hero + trending + prompts)
│   │   ├── shop/page.tsx             # Shop page (filterable product grid)
│   │   ├── curio/page.tsx            # Curio AI chat page
│   │   ├── profile/page.tsx          # Style profile page
│   │   └── globals.css
│   ├── components/
│   │   ├── layout/Sidebar.tsx        # Left nav sidebar
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   └── TypingIndicator.tsx
│   │   ├── products/
│   │   │   ├── ProductCard.tsx
│   │   │   └── InlineProducts.tsx
│   │   ├── preferences/
│   │   │   └── PreferencePanel.tsx
│   │   └── visual-search/
│   │       └── AttributeTags.tsx
│   ├── services/api.ts               # fetch wrapper + SSE generator
│   ├── hooks/use-chat.ts             # Chat state machine
│   └── Dockerfile
│
├── docs/
│   ├── ps.md                         # Hackathon problem statement
│   ├── product.md
│   └── technical.md
├── docker-compose.yml
└── README.md
```

---

## API Reference

### `POST /api/v1/chat`

Streams an AI shopping assistant response as Server-Sent Events.

**Request body:**
```json
{
  "prompt": "I need a casual outfit for a weekend brunch",
  "session_id": "abc123",
  "messages": [
    { "role": "user", "content": "previous turn" },
    { "role": "assistant", "content": "previous reply" }
  ]
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

Analyzes an uploaded image with Gemma4:26b and returns matched products.

**Request:** `multipart/form-data` with `file` field (JPEG/PNG/WEBP, max 5 MB)

**Response:**
```json
{
  "attributes": {
    "style": ["casual", "minimal"],
    "colors": ["white", "navy"],
    "silhouette": "relaxed",
    "category": "tops",
    "material_guess": "cotton",
    "occasion": ["casual", "everyday"],
    "description": "A clean minimal casual top"
  },
  "products": [ ...Product[] ]
}
```

---

### `GET /api/v1/products?category=tops&limit=20`

Returns filtered products from the mock catalog.

---

### `GET /api/v1/preferences/{session_id}`

Returns the current extracted preference state for a session.

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
  category: string;        // tops | bottoms | dresses | outerwear | shoes | accessories
  colors: string[];
  sizes: string[];
  style: string[];
  tags: string[];
  description: string;
  rating: number;
  reviews_count: number;
}
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
    }
  }
}
```

---

## Preference Extraction

Extracted synchronously after each assistant response using regex + keyword matching. No extra LLM call required.

| Field | Method |
|---|---|
| `style` | matched against 20 style keywords |
| `colors` | matched against 23 color keywords |
| `occasions` | matched against 10 occasion keywords |
| `sizes` | regex: `\b(xs|s|m|l|xl|xxl|\d{2})\b` |
| `budget_max` | regex: `(under|below|max)\s*[$₹]?(\d+)` |

---

## Product Matching Algorithm

| Match type | Score |
|---|---|
| Category in text | +4 |
| Style in text | +3 |
| Style in preferences | +2 |
| Color in text | +2 |
| Color in preferences | +2 |
| Tag in text | +1 |
| Price > budget_max | -10 |

Top 6 products by score are returned in the `metadata` SSE event.

---

## Environment Variables

### `backend/.env`
```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_MODEL=gpt-4o
OLLAMA_BASE_URL=http://100.127.36.42:11434
OLLAMA_VISION_MODEL=gemma4:26b
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

## Running with Docker

```bash
cp backend/.env.example backend/.env
# Add your Azure OpenAI credentials

docker-compose up --build
# Frontend → http://localhost:3000
# Backend  → http://localhost:8000
# API docs → http://localhost:8000/docs
```
