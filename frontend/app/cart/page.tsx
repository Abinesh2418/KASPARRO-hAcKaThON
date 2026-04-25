"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Trash2, ShoppingBag, MessageCircle } from "lucide-react";
import { useCart } from "@/hooks/use-cart";
import { formatPrice } from "@/lib/utils";

export default function CartPage() {
  const router = useRouter();
  const { items, loading, loadCart, remove, total } = useCart();
  const [userName, setUserName] = useState("");

  useEffect(() => {
    if (typeof window === "undefined") return;
    const raw = localStorage.getItem("curio_user");
    if (!raw) { router.push("/login"); return; }
    const user = JSON.parse(raw);
    setUserName(user.name ?? user.username);
    loadCart();
  }, [loadCart, router]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-zinc-950">
        <div className="h-6 w-6 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  return (
    <div className="h-full bg-zinc-950 overflow-y-auto">
      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-zinc-100">Your Bag</h1>
          <p className="text-sm text-zinc-500 mt-1">{userName ? `Logged in as ${userName}` : ""}</p>
        </div>

        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="h-16 w-16 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4">
              <ShoppingBag className="h-7 w-7 text-zinc-600" />
            </div>
            <p className="text-zinc-400 font-medium">Your bag is empty</p>
            <p className="text-zinc-600 text-sm mt-1">Ask Curio to recommend something for you</p>
            <button
              onClick={() => router.push("/curio")}
              className="mt-6 flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium px-5 py-2.5 rounded-xl transition-colors"
            >
              <MessageCircle className="h-4 w-4" />
              Open Curio AI
            </button>
          </div>
        ) : (
          <>
            {/* Items */}
            <div className="flex flex-col gap-3">
              {items.map((item) => (
                <div
                  key={item.product_id}
                  className="flex gap-4 bg-zinc-900 border border-zinc-800 rounded-2xl p-4 hover:border-zinc-700 transition-colors"
                >
                  <div className="relative h-20 w-20 flex-shrink-0 rounded-xl overflow-hidden bg-zinc-800">
                    <Image
                      src={item.image || "https://placehold.co/80x80?text=Item"}
                      alt={item.title}
                      fill
                      className="object-cover"
                      sizes="80px"
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-zinc-100 leading-tight">{item.title}</p>
                    {item.size && (
                      <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded-md mt-1 inline-block">
                        Size: {item.size}
                      </span>
                    )}
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-zinc-100">{formatPrice(item.price)}</span>
                        {item.quantity > 1 && (
                          <span className="text-xs text-zinc-500">× {item.quantity}</span>
                        )}
                      </div>
                      <button
                        onClick={() => remove(item.product_id)}
                        className="p-1.5 rounded-lg text-zinc-600 hover:text-red-400 hover:bg-red-950/30 transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="mt-6 bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-zinc-400">
                  {items.reduce((s, i) => s + i.quantity, 0)} item{items.reduce((s, i) => s + i.quantity, 0) !== 1 ? "s" : ""}
                </span>
                <span className="text-lg font-bold text-zinc-100">{formatPrice(total)}</span>
              </div>
              <button className="w-full bg-violet-600 hover:bg-violet-500 text-white font-semibold rounded-xl py-3 text-sm transition-colors shadow-lg shadow-violet-900/30">
                Proceed to Checkout
              </button>
              <button
                onClick={() => router.push("/curio")}
                className="w-full mt-2 text-zinc-400 hover:text-zinc-100 text-sm py-2 transition-colors"
              >
                Continue Shopping with Curio
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
