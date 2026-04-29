"use client";

import { useRef, useState } from "react";
import { ChevronLeft, ChevronRight, ShoppingBag, Check } from "lucide-react";
import { ProductCard } from "./ProductCard";
import { addToCart } from "@/services/api";
import type { Product } from "@/types";

interface Props {
  products: Product[];
  title?: string;
}

export function InlineProducts({ products, title }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [addingAll, setAddingAll] = useState(false);
  const [allAdded, setAllAdded] = useState(false);

  const scroll = (dir: "left" | "right") => {
    scrollRef.current?.scrollBy({ left: dir === "right" ? 200 : -200, behavior: "smooth" });
  };

  const handleAddAll = async () => {
    setAddingAll(true);
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem("curio_user") : null;
      const username = raw ? JSON.parse(raw).username : "guest";
      for (const product of products) {
        await addToCart({
          username,
          product_id: product.id,
          title: product.title,
          price: product.price,
          image: product.images[0] ?? "",
          size: null,
          variant_id: product.variant_id,
          merchant_url: product.merchant_url,
          merchant_name: product.merchant_name,
        });
      }
      setAllAdded(true);
      setTimeout(() => setAllAdded(false), 2500);
    } catch (err) {
      console.error("Add all failed:", err);
    } finally {
      setAddingAll(false);
    }
  };

  if (products.length === 0) return null;

  return (
    <div className="rounded-2xl border border-zinc-700/40 bg-zinc-900/50 p-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">
          {title ?? `${products.length} recommendation${products.length > 1 ? "s" : ""}`}
        </p>
        <div className="flex items-center gap-2">
          {/* Add all button */}
          {products.length > 1 && (
            <button
              onClick={handleAddAll}
              disabled={addingAll || allAdded}
              className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg transition-all ${
                allAdded
                  ? "bg-emerald-600/20 text-emerald-400 border border-emerald-600/30"
                  : "bg-violet-600/20 text-violet-300 border border-violet-500/30 hover:bg-violet-600/30"
              }`}
            >
              {allAdded ? (
                <><Check className="h-3 w-3" /> All added</>
              ) : addingAll ? (
                <><div className="h-3 w-3 rounded-full border border-violet-400 border-t-transparent animate-spin" /> Adding…</>
              ) : (
                <><ShoppingBag className="h-3 w-3" /> Add all</>
              )}
            </button>
          )}
          {/* Scroll buttons */}
          <button
            onClick={() => scroll("left")}
            className="h-6 w-6 rounded-full border border-zinc-700 flex items-center justify-center text-zinc-400 hover:text-zinc-100 hover:border-zinc-500 transition-colors"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => scroll("right")}
            className="h-6 w-6 rounded-full border border-zinc-700 flex items-center justify-center text-zinc-400 hover:text-zinc-100 hover:border-zinc-500 transition-colors"
          >
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide snap-x snap-mandatory"
        style={{ scrollbarWidth: "none" }}
      >
        {products.map((product) => (
          <div key={product.id} className="snap-start flex-shrink-0">
            <ProductCard product={product} compact />
          </div>
        ))}
      </div>
    </div>
  );
}
