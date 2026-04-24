# Kasparo — AI Fashion Shopping Agent

An AI-powered personal shopping assistant that helps users discover fashion through natural conversation and visual search. Describe your vibe, upload a photo, and the AI finds the right products — learning your taste as you talk.

Built for the **Kasparro Agentic Commerce Hackathon (Track 1)** · April 2026

---

## What We Built

A full-stack AI shopping platform with:

- **Curio AI Chat** — Conversational shopping assistant powered by Azure OpenAI (GPT-4o). Ask in plain language, get curated product recommendations with reasoning.
- **Visual Search** — Upload any outfit photo and the AI (Gemma4:26b via Ollama) extracts style attributes and finds similar products.
- **Live Style Profile** — Preferences (style, colors, budget, occasions, size) are learned automatically from the conversation and displayed in real-time.
- **Product Catalog** — 20 curated fashion products across 6 categories with filtering, search, and an AI-matched recommendations engine.
- **Dashboard UI** — Left sidebar navigation with Home, Shop, Curio AI, and Profile pages.

---

## How It Works

1. **Chat** — Tell Curio what you're looking for in plain language
2. **Get recommendations** — Products appear inline in the conversation, matched by style, color, and budget
3. **Upload a photo** — Visual AI extracts the style and finds similar items
4. **Watch your style profile build** — Preferences update in real-time as you chat
5. **Browse the catalog** — Shop page with category and style filters

---

## Quick Start (Docker)

```bash
cp backend/.env.example backend/.env
# → Add your Azure OpenAI credentials to backend/.env

docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React 19, TypeScript, Tailwind CSS v4 |
| UI Components | Radix UI, Lucide icons, Framer Motion |
| Backend | FastAPI, Uvicorn, Pydantic v2 |
| Chat LLM | Azure OpenAI — `gpt-4o` |
| Vision LLM | Ollama — `gemma4:26b` |
| Streaming | Server-Sent Events (SSE) |
| Product data | Mock catalog (20 curated items) |
| Session state | In-memory |

---

## Project Structure

```
kasparo/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # chat, products, visual-search, preferences, health
│   │   ├── services/        # azure_service, ollama_service, product_service, preference_service
│   │   ├── schemas/         # Pydantic models
│   │   └── core/            # config, middleware
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/                 # Home (/), Shop (/shop), Curio (/curio), Profile (/profile)
│   ├── components/          # chat/, products/, preferences/, layout/
│   ├── services/            # api.ts (fetch + SSE)
│   ├── hooks/               # use-chat.ts
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
| `OLLAMA_VISION_MODEL` | Yes | Vision model name (`gemma4:26b`) |

---

## Team

| Role | Person |
|---|---|
| Backend / Full-stack | Abinesh B |
| Frontend / AI | Claude (AI) |
