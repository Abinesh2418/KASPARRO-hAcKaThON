"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Sparkles, Zap, Heart, TrendingUp } from "lucide-react";
import { ProductCard } from "@/components/products/ProductCard";
import { fetchProducts } from "@/services/api";
import type { Product } from "@/types";

const CATEGORIES = ["tops", "bottoms", "dresses", "outerwear", "shoes", "accessories"];

const QUICK_PROMPTS = [
  { label: "Office looks for the week", icon: "💼", color: "from-blue-900/40 to-indigo-900/40 border-blue-700/30" },
  { label: "Date night outfit ideas", icon: "✨", color: "from-rose-900/40 to-pink-900/40 border-rose-700/30" },
  { label: "Beach vacation wardrobe", icon: "🌊", color: "from-cyan-900/40 to-teal-900/40 border-cyan-700/30" },
  { label: "Minimal everyday basics", icon: "🤍", color: "from-zinc-800/60 to-zinc-900/60 border-zinc-700/30" },
];

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts().then((data) => {
      setProducts(data);
      setLoading(false);
    });
  }, []);

  const trending = products.slice(0, 6);

  return (
    <div className="h-full overflow-y-auto">
      {/* Hero */}
      <section className="relative px-6 lg:px-10 pt-12 pb-10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-950/40 via-zinc-950 to-zinc-950 pointer-events-none" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-violet-900/30 border border-violet-700/40 rounded-full px-3 py-1 mb-5">
            <Sparkles className="h-3 w-3 text-violet-400" />
            <span className="text-xs text-violet-300 font-medium">AI-Powered Fashion Discovery</span>
          </div>
          <h1 className="text-4xl lg:text-5xl font-black text-zinc-100 leading-tight mb-4">
            Dress Smarter.
            <br />
            <span className="bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
              Shop Shopify.
            </span>
          </h1>
          <p className="text-zinc-400 text-base lg:text-lg mb-8 max-w-lg">
            Tell Curio your vibe and it finds fashion that fits — your style, budget, and occasion, all in one conversation.
          </p>
          <div className="flex items-center gap-3 flex-wrap">
            <Link
              href="/curio"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white font-semibold px-5 py-2.5 rounded-xl transition-all shadow-lg shadow-violet-900/30 hover:shadow-violet-900/50 hover:-translate-y-0.5"
            >
              <Zap className="h-4 w-4" />
              Ask Curio
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/shop"
              className="inline-flex items-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-100 font-medium px-5 py-2.5 rounded-xl transition-all border border-zinc-700/60"
            >
              Browse All
            </Link>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="px-6 lg:px-10 pb-8">
        <div className="grid grid-cols-3 gap-4 max-w-lg">
          {[
            { value: "20+", label: "Curated Pieces" },
            { value: "AI", label: "Style Matching" },
            { value: "6", label: "Categories" },
          ].map(({ value, label }) => (
            <div key={label} className="bg-zinc-900/60 border border-zinc-800/60 rounded-xl px-4 py-3 text-center">
              <p className="text-lg font-bold text-violet-400">{value}</p>
              <p className="text-[11px] text-zinc-500 mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Trending Now */}
      <section className="px-6 lg:px-10 pb-10">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-violet-400" />
            <h2 className="text-base font-bold text-zinc-100">Trending Now</h2>
          </div>
          <Link href="/shop" className="text-xs text-violet-400 hover:text-violet-300 flex items-center gap-1 transition-colors">
            View all <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-64 rounded-2xl bg-zinc-800/60 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
            {trending.map((product) => (
              <ProductCard key={product.id} product={product} compact />
            ))}
          </div>
        )}
      </section>

      {/* Shop by Category */}
      <section className="px-6 lg:px-10 pb-10">
        <h2 className="text-base font-bold text-zinc-100 mb-5">Shop by Category</h2>
        <div className="flex flex-wrap gap-3">
          {CATEGORIES.map((cat) => (
            <Link
              key={cat}
              href={`/shop?category=${cat}`}
              className="capitalize px-4 py-2 rounded-xl bg-zinc-800/80 border border-zinc-700/60 text-zinc-300 text-sm font-medium hover:bg-violet-900/30 hover:border-violet-500/40 hover:text-violet-300 transition-all"
            >
              {cat}
            </Link>
          ))}
        </div>
      </section>

      {/* Quick Prompts */}
      <section className="px-6 lg:px-10 pb-12">
        <div className="flex items-center gap-2 mb-5">
          <Heart className="h-4 w-4 text-violet-400" />
          <h2 className="text-base font-bold text-zinc-100">Try asking Curio</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {QUICK_PROMPTS.map(({ label, icon, color }) => (
            <Link
              key={label}
              href="/curio"
              className={`group bg-gradient-to-br ${color} border rounded-2xl p-4 hover:scale-[1.02] transition-all duration-200 cursor-pointer`}
            >
              <span className="text-2xl mb-3 block">{icon}</span>
              <p className="text-sm font-medium text-zinc-200 group-hover:text-white transition-colors leading-snug">
                {label}
              </p>
              <div className="mt-3 flex items-center gap-1 text-violet-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Ask Curio</span>
                <ArrowRight className="h-3 w-3" />
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
