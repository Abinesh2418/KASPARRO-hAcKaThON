# Dashboard UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add left sidebar navigation and redesign frontend into Home / Shop / Curio / Profile pages showing the 20 mock products.

**Architecture:** Left sidebar (fixed, icon+label) wraps all pages via root layout. Home shows hero + trending products. Shop shows filterable product grid. Curio hosts the existing chat. Profile shows style card.

**Tech Stack:** Next.js App Router, Tailwind CSS v4, lucide-react, framer-motion

---

### Task 1: Add fetchProducts to services/api.ts
- Modify: `frontend/services/api.ts`
- [ ] Add fetchProducts function calling GET /api/v1/products

### Task 2: Create Sidebar component
- Create: `frontend/components/layout/Sidebar.tsx`
- [ ] Left nav with Home, Shop, Curio, Profile — usePathname for active state

### Task 3: Update root layout with Sidebar
- Modify: `frontend/app/layout.tsx`
- Modify: `frontend/app/globals.css`
- [ ] Wrap children with Sidebar, fix overflow handling

### Task 4: Redesign Home page
- Modify: `frontend/app/page.tsx`
- [ ] Hero + Trending Now + Shop by Category + Quick Prompts

### Task 5: Create Shop page
- Create: `frontend/app/shop/page.tsx`
- [ ] Filterable product grid, all 20 products

### Task 6: Create Curio page + update ChatInterface
- Create: `frontend/app/curio/page.tsx`
- Modify: `frontend/components/chat/ChatInterface.tsx`
- [ ] Move chat to /curio, fix h-screen → h-full

### Task 7: Create Profile page
- Create: `frontend/app/profile/page.tsx`
- [ ] Beautiful style profile card UI
