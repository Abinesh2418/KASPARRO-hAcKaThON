"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { SlidersHorizontal, Search } from "lucide-react";
import { ProductCard } from "@/components/products/ProductCard";
import { fetchProducts } from "@/services/api";
import { cn } from "@/lib/utils";
import type { Product } from "@/types";

const CATEGORIES = ["all", "tops", "bottoms", "dresses", "outerwear", "shoes", "accessories"];
const STYLES = ["minimal", "casual", "formal", "streetwear", "romantic", "athletic", "bohemian", "classic"];

function ShopContent() {
  const searchParams = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState(searchParams.get("category") ?? "all");
  const [activeStyle, setActiveStyle] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchProducts().then((data) => {
      setProducts(data);
      setLoading(false);
    });
  }, []);

  const filtered = products.filter((p) => {
    const matchesCategory = activeCategory === "all" || p.category === activeCategory;
    const matchesStyle = !activeStyle || p.style.includes(activeStyle);
    const matchesSearch =
      !search ||
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.tags.some((t) => t.includes(search.toLowerCase()));
    return matchesCategory && matchesStyle && matchesSearch;
  });

  return (
    <div className="h-full overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-zinc-950/90 backdrop-blur-sm border-b border-zinc-800/60 px-6 lg:px-10 py-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h1 className="text-lg font-bold text-zinc-100">Shop</h1>
            <p className="text-xs text-zinc-500">{filtered.length} items</p>
          </div>
          <div className="flex items-center gap-2 bg-zinc-800/80 border border-zinc-700/60 rounded-xl px-3 py-2 w-48 lg:w-64">
            <Search className="h-3.5 w-3.5 text-zinc-500 flex-shrink-0" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search styles..."
              className="bg-transparent text-sm text-zinc-300 placeholder-zinc-600 outline-none w-full"
            />
          </div>
        </div>

        {/* Category filters */}
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={cn(
                "flex-shrink-0 capitalize px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                activeCategory === cat
                  ? "bg-violet-600 text-white shadow-sm shadow-violet-900/40"
                  : "bg-zinc-800/60 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
              )}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Style filters */}
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1 mt-2">
          <div className="flex items-center gap-1 flex-shrink-0 text-zinc-600">
            <SlidersHorizontal className="h-3 w-3" />
            <span className="text-[10px]">Style:</span>
          </div>
          {STYLES.map((style) => (
            <button
              key={style}
              onClick={() => setActiveStyle(activeStyle === style ? null : style)}
              className={cn(
                "flex-shrink-0 capitalize px-3 py-1 rounded-lg text-[11px] font-medium transition-all border",
                activeStyle === style
                  ? "border-violet-500/60 bg-violet-900/30 text-violet-300"
                  : "border-zinc-700/40 text-zinc-500 hover:border-zinc-600 hover:text-zinc-300"
              )}
            >
              {style}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      <div className="px-6 lg:px-10 py-6">
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="h-72 rounded-2xl bg-zinc-800/60 animate-pulse" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <p className="text-4xl mb-4">🔍</p>
            <p className="text-zinc-400 font-medium">No items found</p>
            <p className="text-zinc-600 text-sm mt-1">Try a different filter or search term</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filtered.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ShopPage() {
  return (
    <Suspense>
      <ShopContent />
    </Suspense>
  );
}
