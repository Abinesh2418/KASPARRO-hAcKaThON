# Curio — Product Overview

**Curio** is an AI-powered personal shopping assistant built for Indian fashion shoppers. Instead of scrolling through hundreds of listings, users describe what they want in plain language — and Curio finds the right products, explains its reasoning, and learns their taste with every message.

Built for the **Kasparro Agentic Commerce Hackathon — Track 1**

---

## Problem It Solves

Traditional product discovery forces users through a tedious loop:

**Search → Filter → Browse → Compare → Read reviews → Decide → Add to cart → Checkout**

Curio collapses this into a single conversation.

---

## Target Users

- Fashion-conscious shoppers who want curation, not keyword matching
- Busy buyers who want outfit recommendations without browsing fatigue
- Style explorers who want to describe a vibe and get exact matches
- Gift shoppers who need help choosing for someone they don't know well

---

## Features

### Feature 1 — Conversational Shopping

Users describe what they're looking for in natural language — "something minimal but interesting for a job interview next week" — and Curio responds like a knowledgeable personal stylist. No filters, no dropdowns. Just a conversation.

Curio asks smart follow-up questions (budget → occasion → style) one at a time, never overwhelming the user, and only asks what it actually needs to narrow the recommendation. Users can also refine mid-conversation: "show me cheaper ones", "in navy instead", "more minimal please" — and Curio adjusts without losing context.

### Feature 2 — Multi-Agent AI Reasoning Pipeline

Behind every recommendation is an 8-step reasoning pipeline:

1. **Intent Agent** — Classifies what the user wants (11 intent types: shopping, cart, checkout, refinement, gift, comparison, and more)
2. **Search Agent** — Generates optimized search queries from intent
3. **Product Fetch** — Pulls live candidates from ALL configured Shopify stores in parallel
4. **Compare & Rank Agent** — Scores products across occasion fit, style match, budget fit, and category relevance (0–100 scale, threshold 35)
5. **Explain Agent** — Generates stylist-quality reasoning for each pick
6. **Response** — Streams the final conversational answer to the user
7. **Tradeoff Agent** — Runs after the response for single-product queries; scores top 3 picks across 7 dimensions and generates Best Fit / Best Value comparison panels

This is not keyword matching — it is multi-step reasoning on live inventory.

### Feature 3 — Explainable Picks

Every recommendation comes with a brief, stylist-quality rationale:

- *"Structured cut reads professional without feeling stiff — great for interviews"*
- *"₹400 over budget but the fabric quality justifies it for a one-time event"*

The AI never recommends without explaining why.

### Feature 4 — Real-Time Streaming Responses

Curio's replies appear word-by-word as the AI generates them — instant feedback, not a loading spinner. The experience feels live, not like waiting for a server.

### Feature 5 — Inline Product Recommendations

When Curio mentions specific items, product cards appear directly inside the chat — with images, prices, and size selectors. Users never have to leave the conversation to browse.

### Feature 6 — Visual Style Search

Users upload any fashion photo — a screenshot from Instagram, Pinterest, or Myntra; a photo of clothing they already own; a runway look — and Curio extracts the style, color palette, silhouette, and occasion using multimodal AI. It then surfaces matching products from the catalog.

### Feature 7 — Live Style Profile

As the conversation progresses, Curio quietly extracts preferences — preferred colors, styles, occasions, and budget — and displays them in a real-time Style Profile panel. Users can see exactly what the AI has learned about their taste.

### Feature 8 — Multi-Turn Conversation Memory

Curio remembers the full conversation within a session. If a user says "actually, I prefer navy" five messages later, the AI recalibrates all subsequent recommendations — no need to repeat context.

### Feature 9 — Cart Management

Users can add products to a cart directly from the conversation or inline product cards. The AI understands natural add commands:

- Ordinal references — "add the first one", "add the second one in size M"
- Named items — "add the kurta and the mojaris"
- Confirmations — "yes please", "I'll take it"

If the user's size is unavailable, the agent picks the closest available size and flags it. The cart persists per user via the backend.

### Feature 10 — Conversational Checkout

When the user is ready to buy, they just say so — "I'm done", "checkout", "ready to pay", "bas itna hi" — and Curio handles the rest in the chat.

The AI validates the cart, generates an inline cart summary card with all items grouped by merchant, and presents a one-tap checkout button per store. Checkout URLs are generated live via Shopify's cartCreate API.

*Example:*
> User: "Take me to checkout"
> Curio: Shows cart summary card → "Two checkouts coming up — Veda first (₹1,499), then Indie (₹1,299)"

### Feature 11 — Multi-Merchant Checkout

Curio supports products from multiple Shopify merchants in a single conversation. When a cart has items from different stores, it:

- Groups items by merchant in the checkout summary card
- Generates a separate Shopify checkout URL for each store
- Presents numbered checkout buttons ("Step 1 of 2 — Checkout with Veda")
- Gently warns users when adding items from a different store than what's already in their cart

### Feature 12 — Photo Upload with Preview

Users upload a photo in the chat input bar. A thumbnail preview appears before submission, and a loading indicator is shown while the AI analyzes the image.

### Feature 13 — Visual Tradeoff Matrix

After every single-product recommendation, Curio renders a live **Visual Tradeoff Matrix** directly inside the chat. It shows:

- An animated score breakdown table for the top 3 picks across 7 dimensions (occasion fit, style match, budget fit, category, color, availability, value)
- Two summary panels — **Best Fit** (highest occasion + style score) and **Best Value** (highest value + budget score)
- Quick-reply buttons in each panel: "Add to cart", "Find cheaper options", "Show similar styles"
- Contextual cart labels — e.g. "Add Best Value — Minimalist Silver Mesh Watch"

Score bars animate from 0 on load with emerald → amber → red gradient based on percentage. Total out of 135 shown with colored accents per rank.

---

## Value Proposition

| Traditional Search | Curio AI |
|---|---|
| User must know what to search | User describes intent in plain language |
| Filter by price / category | AI learns preferences naturally |
| Static product grid | Products appear inside the conversation |
| No reasoning behind results | Every pick explained with styling rationale |
| Text search only | Text + image search |
| US-centric defaults | Native ₹ budgets, Indian occasions, Indian categories |
| No memory between sessions | Style profile builds across the conversation |
| Manual cart + checkout flow | Add to cart and checkout from the conversation |
| Single-store only | Multi-merchant: discover and buy from multiple Shopify stores in one chat |
| Hidden scoring criteria | Visual Tradeoff Matrix shows why each product ranks where it does |

---

## Team

**Duo Dominators**

| Role | Person |
|---|---|
| Backend / Full-stack | Abinesh B |
| Frontend / UI | Ambika S |
