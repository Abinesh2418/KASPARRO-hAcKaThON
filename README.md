# Kasparo — AI Fashion Shopping Agent

An AI-powered personal shopping assistant that helps users discover fashion through natural conversation and visual search. Describe your vibe, upload a photo, and the AI finds the right products — learning your taste as you talk.

Built for the **Kasparro Agentic Commerce Hackathon (Track 1)** · April 2026

---

## What We Built

A full-stack AI shopping platform with:

- **Curio AI Chat** — Conversational shopping assistant powered by a 6-agent Azure OpenAI (GPT-4o) pipeline. Ask in plain language, get curated product recommendations with stylist-quality reasoning.
- **Visual Search** — Upload any outfit photo and the AI (Ollama vision) extracts style attributes and finds similar products from the live Shopify catalog.
- **Live Style Profile** — Preferences (style, colors, budget, occasions, size) are learned automatically from the conversation and displayed in real-time.
- **Cart Management** — Add products directly from the conversation. Cart persists per user across sessions.
- **User Auth** — Simple login with session-scoped cart and preferences.
- **Indian Market Context** — Native ₹ budgets, Indian occasions, Indian fashion categories, and Hinglish understanding.

---

## How It Works

1. **Chat** — Tell Curio what you're looking for in plain language
2. **6-agent pipeline** — Intent → Search → Fetch → Compare → Explain → Respond
3. **Get recommendations** — Products appear inline in the conversation, matched and ranked by occasion fit, style, and budget
4. **Upload a photo** — Visual AI extracts the style and finds similar items
5. **Watch your style profile build** — Preferences update in real-time as you chat
6. **Add to cart** — One tap from the conversation or product card

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
SHOPIFY_STORE_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_storefront_token
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
| Product Data | Shopify Storefront GraphQL API (fallback: mock catalog) |
| Streaming | Server-Sent Events (SSE) |
| Session State | In-memory |

---

## Project Structure

```
kasparo/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # chat, products, visual-search, preferences, auth, cart, health
│   │   ├── services/        # orchestrator, llm, azure, ollama, shopify, product, preference
│   │   ├── schemas/         # Pydantic models
│   │   └── core/            # config, middleware, prompts (6 agent prompts)
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
| `SHOPIFY_STORE_URL` | Yes | Shopify store URL |
| `SHOPIFY_ACCESS_TOKEN` | Yes | Shopify Storefront API token |

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
