"use client";

import { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { ProductCard } from "./ProductCard";
import type { Product } from "@/types";

interface Props {
  products: Product[];
  title?: string;
}

export function InlineProducts({ products, title }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const scroll = (dir: "left" | "right") => {
    scrollRef.current?.scrollBy({ left: dir === "right" ? 200 : -200, behavior: "smooth" });
  };

  if (products.length === 0) return null;

  return (
    <div className="rounded-2xl border border-zinc-700/40 bg-zinc-900/50 p-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold text-violet-400 uppercase tracking-wider">
          {title ?? `${products.length} recommendation${products.length > 1 ? "s" : ""}`}
        </p>
        <div className="flex gap-1">
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
