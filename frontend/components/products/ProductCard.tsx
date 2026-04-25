"use client";

import { useState } from "react";
import Image from "next/image";
import { Star, ShoppingBag } from "lucide-react";
import { cn, formatPrice } from "@/lib/utils";
import type { Product } from "@/types";
import { addToCart } from "@/services/api";

interface Props {
  product: Product;
  compact?: boolean;
}

export function ProductCard({ product, compact = false }: Props) {
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [added, setAdded] = useState(false);

  const handleAddToCart = async () => {
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem("curio_user") : null;
      const username = raw ? JSON.parse(raw).username : "guest";
      await addToCart({
        username,
        product_id: product.id,
        title: product.title,
        price: product.price,
        image: product.images[0] ?? "",
        size: selectedSize,
      });
    } catch {
      // silently fail — still show feedback
    }
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };

  const discount = product.compare_at_price
    ? Math.round((1 - product.price / product.compare_at_price) * 100)
    : null;

  return (
    <div
      className={cn(
        "group relative flex flex-col rounded-2xl overflow-hidden border border-zinc-700/50 bg-zinc-900 hover:border-violet-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-violet-900/10",
        compact ? "w-44" : "w-full"
      )}
    >
      {/* Product Image */}
      <div className={cn("relative overflow-hidden bg-zinc-800", compact ? "h-52" : "h-64")}>
        <Image
          src={product.images[0]}
          alt={product.title}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-500"
          sizes={compact ? "176px" : "300px"}
        />
        {discount && (
          <span className="absolute top-2 left-2 bg-violet-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
            -{discount}%
          </span>
        )}
        {/* Color dots */}
        <div className="absolute bottom-2 left-2 flex gap-1">
          {product.colors.slice(0, 4).map((color) => (
            <span
              key={color}
              className="text-[9px] bg-black/60 text-zinc-300 px-1.5 py-0.5 rounded-full backdrop-blur-sm"
            >
              {color}
            </span>
          ))}
        </div>
      </div>

      {/* Info */}
      <div className="flex flex-col gap-2 p-3">
        <div>
          <h3 className={cn("font-medium text-zinc-100 leading-tight", compact ? "text-xs" : "text-sm")}>
            {product.title}
          </h3>
          {!compact && (
            <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2">{product.description}</p>
          )}
        </div>

        {/* Rating */}
        <div className="flex items-center gap-1">
          <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
          <span className="text-xs text-zinc-400">
            {product.rating} ({product.reviews_count.toLocaleString()})
          </span>
        </div>

        {/* Sizes (compact hides this) */}
        {!compact && product.sizes.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {product.sizes.slice(0, 5).map((size) => (
              <button
                key={size}
                onClick={() => setSelectedSize(size === selectedSize ? null : size)}
                className={cn(
                  "text-[10px] px-2 py-0.5 rounded-md border transition-colors",
                  selectedSize === size
                    ? "border-violet-500 bg-violet-900/30 text-violet-300"
                    : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                )}
              >
                {size}
              </button>
            ))}
          </div>
        )}

        {/* Price + CTA */}
        <div className="flex items-center justify-between mt-auto pt-1">
          <div className="flex items-baseline gap-1.5">
            <span className={cn("font-bold text-zinc-100", compact ? "text-sm" : "text-base")}>
              {formatPrice(product.price)}
            </span>
            {product.compare_at_price && (
              <span className="text-xs text-zinc-500 line-through">
                {formatPrice(product.compare_at_price)}
              </span>
            )}
          </div>

          <button
            onClick={handleAddToCart}
            className={cn(
              "flex items-center gap-1 rounded-xl px-3 py-1.5 text-xs font-medium transition-all",
              added
                ? "bg-emerald-600 text-white"
                : "bg-violet-600 hover:bg-violet-500 text-white shadow-sm"
            )}
          >
            <ShoppingBag className="h-3.5 w-3.5" />
            {added ? "Added!" : compact ? "Add" : "Add to bag"}
          </button>
        </div>
      </div>
    </div>
  );
}
