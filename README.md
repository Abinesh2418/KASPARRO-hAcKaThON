# Kasparo — AI Fashion Shopping Agent

An AI-powered personal shopping assistant that helps users discover fashion through natural conversation and visual search. Describe your vibe, upload a photo, and the AI finds the right products — learning your taste as you talk.

Built for the **Kasparro Agentic Commerce Hackathon (Track 1)** · April 2026

---

## What We Built

A full-stack AI shopping platform with:

- **Curio AI Chat** — Conversational shopping assistant powered by an agent pipeline (Azure OpenAI GPT-4o). Ask in plain language, get curated product recommendations with stylist-quality reasoning.
- **Visual Search** — Upload any outfit photo and the AI (Ollama vision) extracts style attributes and finds similar products from the live Shopify catalog.
- **Live Style Profile** — Preferences (style, colors, budget, occasions, size) are learned automatically from the conversation and displayed in real-time.
- **Cart Management** — Add products directly from the conversation using natural language ("add the first one in M", "add both").
- **Conversational Checkout** — Say "I'm done" or "checkout" and Curio shows an inline cart summary with real Shopify checkout URLs generated via `cartCreate`.
- **Multi-Merchant Checkout** — Items from multiple Shopify stores are grouped and presented with a separate checkout button per merchant.
- **User Auth** — Simple login with session-scoped cart and preferences.
- **Indian Market Context** — Native ₹ budgets, Indian occasions, Indian fashion categories, and Hinglish understanding.

---

## How It Works

1. **Chat** — Tell Curio what you're looking for in plain language
2. **Agent pipeline** — Intent (11 types) → Search → Fetch → Compare → Explain → Respond
3. **Get recommendations** — Products appear inline in the conversation, matched and ranked by occasion fit, style, and budget
4. **Upload a photo** — Visual AI extracts the style and finds similar items
5. **Watch your style profile build** — Preferences update in real-time as you chat
6. **Add to cart** — By name, ordinal ("the second one"), or confirmation ("yes please")
7. **Checkout from the chat** — "I'm done" → inline cart summary → one-tap checkout per merchant

---

## Getting Started

### Prerequisites

- [Docker + Docker Compose](https://docs.docker.com/get-docker/) — for the containerised setup
- [Python 3.11+](https://www.python.org/) — for local backend
- [Node.js 20+](https://nodejs.org/) — for local frontend
- [Ollama](https://ollama.com/) — running locally or on a network machine with `llama3.2-vision` pulled
- Azure OpenAI resource with a `gpt-4o` deployment
- Shopify Storefront API token

---

### Option 1 — Docker (recommended)

**1. Clone the repo**
```bash
git clone https://github.com/your-org/kasparo.git
cd kasparo
```

**2. Configure environment**
```bash
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in:
```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_MODEL=gpt-4o
OLLAMA_BASE_URL=http://host.docker.internal:11434
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your_admin_token
SHOPIFY_STOREFRONT_TOKEN=your_storefront_token
```

**3. Start Ollama on your host machine**

Ollama runs on the host (not inside Docker). The backend container reaches it via `host.docker.internal:11434`.

```bash
ollama pull llama3.2-vision
ollama serve
```

> On Linux, `host.docker.internal` may not resolve automatically. If so, set `OLLAMA_BASE_URL=http://172.17.0.1:11434` in `backend/.env` (your Docker bridge IP).

**4. Start all services**
```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

### Option 2 — Local (without Docker)

**1. Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env      # then fill in credentials
python run.py
# → running on http://localhost:8000
```

**2. Frontend**
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
# → running on http://localhost:3000
```

**3. Ollama (vision model)**
```bash
ollama pull llama3.2-vision
ollama serve
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| UI Components | Radix UI, Lucide icons, Framer Motion |
| Backend | FastAPI, Uvicorn, Pydantic v2 |
| Chat / Agents LLM | Azure OpenAI — `gpt-4o` |
| Vision LLM | Ollama — `llama3.2-vision:latest` |
| Product Data | Shopify Admin GraphQL API (fallback: mock catalog) |
| Checkout | Shopify Storefront API — `cartCreate` mutation |
| Streaming | Server-Sent Events (SSE) |
| Session State | In-memory |

---

## Project Structure

```
kasparo/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # chat, products, visual-search, preferences, auth, cart, health
│   │   ├── services/        # orchestrator, llm, azure, ollama, shopify, cart, product, preference
│   │   ├── schemas/         # Pydantic models
│   │   └── core/            # config, middleware, prompts (7 agent prompts incl. checkout)
│   ├── db/users.json        # File-based user store
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/                 # Home (/), Login (/login), Curio (/curio), Cart (/cart), Profile (/profile)
│   ├── components/          # chat/, products/, preferences/, visual-search/, layout/
│   ├── hooks/               # use-chat.ts, use-cart.ts
│   ├── services/            # api.ts (fetch + SSE async generator)
│   ├── types/               # index.ts
│   └── Dockerfile
├── docs/
│   ├── ps.md                # Hackathon problem statement
│   ├── product.md           # Product features
│   └── technical.md         # Technical reference
├── docker-compose.yml
└── README.md
```

---

## Environment Variables

**`backend/.env`**

| Variable | Required | Description |
|---|---|---|
| `AZURE_OPENAI_API_KEY` | Yes | Azure OpenAI API key |
| `AZURE_OPENAI_ENDPOINT` | Yes | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_API_VERSION` | Yes | API version (e.g. `2024-12-01-preview`) |
| `AZURE_OPENAI_MODEL` | Yes | Deployment name (e.g. `gpt-4o`) |
| `OLLAMA_BASE_URL` | Yes | Ollama server URL |
| `OLLAMA_VISION_MODEL` | Yes | Vision model name (e.g. `llama3.2-vision:latest`) |
| `SHOPIFY_STORE_URL` | Yes | Shopify store URL (e.g. `your-store.myshopify.com`) |
| `SHOPIFY_ACCESS_TOKEN` | Yes | Shopify Admin API token (product fetch) |
| `SHOPIFY_STOREFRONT_TOKEN` | Yes | Shopify Storefront API token (cartCreate / checkout) |

**`frontend/.env.local`**

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend base URL (default: `http://localhost:8000`) |

---

## Team

| Role | Person |
|---|---|
| Backend / Full-stack | Abinesh B |
| Frontend / UI | Ambika S |
