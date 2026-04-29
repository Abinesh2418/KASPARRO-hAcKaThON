"use client";

import Link from "next/link";
import {
  ArrowRight,
  Sparkles,
  Zap,
  MessageCircle,
  Brain,
  ShoppingCart,
  Camera,
  Target,
  Star,
  Clock,
  Layers,
  Heart,
  BarChart3,
  Store,
  TrendingUp,
  GitCompare,
} from "lucide-react";

const FEATURES = [
  {
    icon: Brain,
    title: "Deep Intent Understanding",
    description:
      "Curio doesn't just keyword-match — it understands what you actually need. Tell it your occasion, budget, and vibe and it reasons about the perfect pick.",
    color: "from-violet-600/20 to-purple-700/10 border-violet-500/20",
    iconColor: "text-violet-400",
    iconBg: "bg-violet-500/10",
  },
  {
    icon: Layers,
    title: "8-Agent AI Pipeline",
    description:
      "Eight specialized AI agents work in sequence: Intent → Search → Fetch → Compare → Explain → Tradeoff → Cart → Checkout. Every recommendation and every purchase is handled end-to-end in one conversation.",
    color: "from-blue-600/20 to-indigo-700/10 border-blue-500/20",
    iconColor: "text-blue-400",
    iconBg: "bg-blue-500/10",
  },
  {
    icon: Target,
    title: "Ranked & Compared",
    description:
      "Products are scored against your intent before you see them. Price vs quality tradeoffs, style fit, and occasion suitability — all evaluated silently.",
    color: "from-emerald-600/20 to-teal-700/10 border-emerald-500/20",
    iconColor: "text-emerald-400",
    iconBg: "bg-emerald-500/10",
  },
  {
    icon: Camera,
    title: "Visual Search",
    description:
      "Upload any outfit photo — from Instagram, Pinterest, or your wardrobe — and Curio finds matching products from the Shopify catalog instantly.",
    color: "from-rose-600/20 to-pink-700/10 border-rose-500/20",
    iconColor: "text-rose-400",
    iconBg: "bg-rose-500/10",
  },
  {
    icon: ShoppingCart,
    title: "Real Shopify Checkout",
    description:
      "Say 'add this' or 'I'm done' and Curio handles the rest — real Shopify cartCreate calls, per-merchant checkout URLs, and an inline cart summary, all inside the chat.",
    color: "from-amber-600/20 to-orange-700/10 border-amber-500/20",
    iconColor: "text-amber-400",
    iconBg: "bg-amber-500/10",
  },
  {
    icon: MessageCircle,
    title: "Explainable Picks",
    description:
      "Curio tells you exactly why it recommends each item — how it fits your style, occasion, and budget — so you shop with confidence, not confusion.",
    color: "from-cyan-600/20 to-sky-700/10 border-cyan-500/20",
    iconColor: "text-cyan-400",
    iconBg: "bg-cyan-500/10",
  },
  {
    icon: BarChart3,
    title: "Visual Tradeoff Matrix",
    description:
      "After every recommendation, Curio renders a live score breakdown across 7 dimensions — occasion fit, style, budget, color, availability and value. See exactly why P1 beats P2 at a glance.",
    color: "from-violet-600/20 to-indigo-700/10 border-violet-500/20",
    iconColor: "text-violet-400",
    iconBg: "bg-violet-500/10",
  },
  {
    icon: Store,
    title: "Multi-Merchant Store",
    description:
      "Shop across multiple Shopify stores in one conversation. Curio discovers products from all merchants simultaneously, compares them on the same scale, and checks out through each store separately.",
    color: "from-fuchsia-600/20 to-pink-700/10 border-fuchsia-500/20",
    iconColor: "text-fuchsia-400",
    iconBg: "bg-fuchsia-500/10",
  },
];

const PROS = [
  {
    icon: Clock,
    label: "Save Hours of Scrolling",
    detail: "One conversation replaces the entire browse → filter → compare loop.",
  },
  {
    icon: Star,
    label: "Indian Fashion Context",
    detail: "Understands kurtas, lehengas, salwars, and Indian occasion dressing natively.",
  },
  {
    icon: Target,
    label: "Budget-Aware Always",
    detail: "Set your budget once. Curio never recommends above it without flagging the tradeoff.",
  },
  {
    icon: Heart,
    label: "Occasion-First Reasoning",
    detail: "Office, college, wedding, festival — Curio styles for the moment, not just the garment.",
  },
  {
    icon: ShoppingCart,
    label: "One-Tap Shopify Checkout",
    detail: "Live checkout URLs via Shopify cartCreate — one per merchant. Add to cart and pay without leaving the conversation.",
  },
  {
    icon: Brain,
    label: "Gets Smarter Each Turn",
    detail: "Curio remembers your preferences within the session and refines with every reply.",
  },
  {
    icon: GitCompare,
    label: "Tradeoff Transparency",
    detail: "Every top pick comes with a visual 7-dimension score matrix — see exactly why one product beats another.",
  },
  {
    icon: TrendingUp,
    label: "Shop Across Stores",
    detail: "Discover and compare products from Nova and Indie in one search. One conversation, multiple merchants.",
  },
];

export default function Home() {
  return (
    <div className="h-full overflow-y-auto">

      {/* Hero */}
      <section className="relative px-6 lg:px-10 pt-12 pb-12 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-950/50 via-zinc-950 to-zinc-950 pointer-events-none" />
        <div className="absolute top-0 left-1/3 w-[500px] h-[500px] bg-violet-600/8 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-64 h-64 bg-purple-700/6 rounded-full blur-2xl pointer-events-none" />

        {/* Team badge — top right */}
        <div className="absolute top-4 right-6 flex items-center gap-2 bg-gradient-to-r from-violet-900/60 to-fuchsia-900/40 border border-violet-500/30 rounded-full px-3 py-1.5 shadow-lg shadow-violet-900/20 backdrop-blur-sm">
          <span className="flex gap-0.5">
            <span className="h-1.5 w-1.5 rounded-full bg-violet-400 animate-pulse" />
            <span className="h-1.5 w-1.5 rounded-full bg-fuchsia-400 animate-pulse [animation-delay:150ms]" />
          </span>
          <span className="text-[11px] font-bold tracking-wide bg-gradient-to-r from-violet-300 to-fuchsia-300 bg-clip-text text-transparent">
            Duo Dominators
          </span>
        </div>

        <div className="relative max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-violet-900/30 border border-violet-700/40 rounded-full px-3 py-1 mb-6">
            <Sparkles className="h-3 w-3 text-violet-400" />
            <span className="text-xs text-violet-300 font-medium">Powered by Multi-Agent AI</span>
          </div>

          <h1 className="text-4xl lg:text-5xl font-black text-zinc-100 leading-tight mb-4 tracking-tight">
            From Intent
            <br />
            <span className="bg-gradient-to-r from-violet-400 via-purple-400 to-fuchsia-400 bg-clip-text text-transparent">
              to Purchase.
            </span>
          </h1>

          <p className="text-zinc-400 text-base lg:text-lg mb-8 max-w-xl leading-relaxed">
            Curio is your AI fashion agent. Describe your occasion, budget, or vibe — it searches, compares, and explains the best picks from Shopify, then adds them to your cart on command.
          </p>

          <div className="flex items-center gap-3 flex-wrap">
            <Link
              href="/curio"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white font-semibold px-6 py-3 rounded-xl transition-all shadow-lg shadow-violet-900/40 hover:shadow-violet-900/60 hover:-translate-y-0.5"
            >
              <Zap className="h-4 w-4" />
              Start with Curio
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="px-6 lg:px-10 pb-12">
        <div className="grid grid-cols-3 gap-4 max-w-sm">
          {[
            { value: "8", label: "AI Agents" },
            { value: "Live", label: "2 Shopify Stores" },
            { value: "∞", label: "Style Combos" },
          ].map(({ value, label }) => (
            <div key={label} className="bg-zinc-900/60 border border-zinc-800/60 rounded-xl px-4 py-3 text-center">
              <p className="text-lg font-bold text-violet-400">{value}</p>
              <p className="text-[11px] text-zinc-500 mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="px-6 lg:px-10 pb-12">
        <div className="mb-7">
          <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-1">What Curio Does</p>
          <h2 className="text-xl font-bold text-zinc-100">Built differently from search</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {FEATURES.map(({ icon: Icon, title, description, color, iconColor, iconBg }) => (
            <div
              key={title}
              className={`bg-gradient-to-br ${color} border rounded-2xl p-5 hover:scale-[1.01] transition-transform duration-200`}
            >
              <div className={`h-9 w-9 rounded-xl ${iconBg} flex items-center justify-center mb-4`}>
                <Icon className={`h-4.5 w-4.5 ${iconColor}`} />
              </div>
              <h3 className="text-sm font-bold text-zinc-100 mb-2">{title}</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Friction loop callout */}
      <section className="px-6 lg:px-10 pb-12">
        <div className="relative rounded-2xl border border-zinc-800/60 bg-zinc-900/40 px-6 py-8 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-violet-950/30 via-transparent to-transparent pointer-events-none" />
          <div className="relative">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-4">The gap Curio closes</p>
            <div className="flex flex-wrap items-center gap-2 mb-5">
              {["searching", "filtering", "comparing", "reading reviews", "deciding", "adding to cart", "checkout"].map((step, i, arr) => (
                <span key={step} className="flex items-center gap-2">
                  <span className="text-sm text-zinc-400 bg-zinc-800/80 border border-zinc-700/50 rounded-lg px-3 py-1.5 font-medium">
                    {step}
                  </span>
                  {i < arr.length - 1 && (
                    <ArrowRight className="h-3.5 w-3.5 text-zinc-600 flex-shrink-0" />
                  )}
                </span>
              ))}
            </div>
            <p className="text-zinc-500 text-sm mb-4">That whole painful loop — gone.</p>
            <p className="text-lg font-bold text-zinc-100">
              <span className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">Intent → Purchase.</span>
              {" "}No friction in between.
            </p>
          </div>
        </div>
      </section>

      {/* Pros */}
      <section className="px-6 lg:px-10 pb-14">
        <div className="mb-7">
          <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-1">Why Curio</p>
          <h2 className="text-xl font-bold text-zinc-100">The smarter way to shop fashion</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {PROS.map(({ icon: Icon, label, detail }) => (
            <div
              key={label}
              className="flex items-start gap-3 bg-zinc-900/50 border border-zinc-800/50 rounded-xl p-4 hover:border-zinc-700/60 transition-colors"
            >
              <div className="h-8 w-8 rounded-lg bg-violet-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Icon className="h-4 w-4 text-violet-400" />
              </div>
              <div>
                <p className="text-sm font-semibold text-zinc-200 mb-0.5">{label}</p>
                <p className="text-xs text-zinc-500 leading-relaxed">{detail}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
}
