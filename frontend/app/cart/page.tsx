"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Trash2, ShoppingBag, MessageCircle, ExternalLink, Store } from "lucide-react";
import { useCart } from "@/hooks/use-cart";
import { cartCheckout, type MerchantCheckoutInfo } from "@/services/api";
import { formatPrice } from "@/lib/utils";
import type { CartItem } from "@/types";

function MerchantSection({
  merchantName,
  items,
  onRemove,
}: {
  merchantName: string;
  items: CartItem[];
  onRemove: (id: string) => void;
}) {
  const subtotal = items.reduce((s, i) => s + i.price * i.quantity, 0);
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden">
      {/* Merchant header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-900/80">
        <div className="flex items-center gap-2">
          <Store className="h-3.5 w-3.5 text-violet-400" />
          <span className="text-xs font-semibold text-violet-400 uppercase tracking-wide">
            {merchantName}
          </span>
        </div>
        <span className="text-xs text-zinc-500">
          {items.reduce((s, i) => s + i.quantity, 0)} item{items.reduce((s, i) => s + i.quantity, 0) !== 1 ? "s" : ""} · {formatPrice(subtotal)}
        </span>
      </div>

      {/* Items */}
      <div className="divide-y divide-zinc-800/60">
        {items.map((item) => (
          <div key={item.product_id} className="flex gap-4 p-4 hover:bg-zinc-800/30 transition-colors">
            <div className="relative h-18 w-18 flex-shrink-0 rounded-xl overflow-hidden bg-zinc-800" style={{ width: 72, height: 72 }}>
              <Image
                src={item.image || "https://placehold.co/72x72?text=Item"}
                alt={item.title}
                fill
                className="object-cover"
                sizes="72px"
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
                  onClick={() => onRemove(item.product_id)}
                  className="p-1.5 rounded-lg text-zinc-600 hover:text-red-400 hover:bg-red-950/30 transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CheckoutButton({
  checkout,
  isMulti,
  total,
  isLoading,
  onClick,
}: {
  checkout: MerchantCheckoutInfo;
  isMulti: boolean;
  total: number;
  isLoading: boolean;
  onClick: (url: string) => void;
}) {
  return (
    <button
      onClick={() => onClick(checkout.checkout_url)}
      disabled={isLoading}
      className="w-full flex items-center justify-between bg-violet-600 hover:bg-violet-500 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold rounded-xl py-3 px-4 text-sm transition-colors shadow-lg shadow-violet-900/30"
    >
      <span>
        {isLoading
          ? "Preparing checkout…"
          : isMulti
          ? `Checkout at ${checkout.merchant_name}`
          : "Proceed to Checkout"}
      </span>
      <span className="flex items-center gap-1.5 text-violet-200">
        {formatPrice(isMulti ? checkout.subtotal : total)}
        <ExternalLink className="h-3.5 w-3.5" />
      </span>
    </button>
  );
}

export default function CartPage() {
  const router = useRouter();
  const { items, loading, loadCart, remove, total } = useCart();
  const [userName, setUserName] = useState("");
  const [username, setUsername] = useState("");
  const [checkouts, setCheckouts] = useState<MerchantCheckoutInfo[]>([]);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const raw = localStorage.getItem("curio_user");
    if (!raw) { router.push("/login"); return; }
    const user = JSON.parse(raw);
    setUserName(user.name ?? user.username);
    setUsername(user.username ?? "guest");
    loadCart();
  }, [loadCart, router]);

  // Group items by merchant
  const merchantGroups = items.reduce<Record<string, CartItem[]>>((acc, item) => {
    const key = item.merchant_name || "Kasparro";
    acc[key] = acc[key] ? [...acc[key], item] : [item];
    return acc;
  }, {});

  const isMultiMerchant = Object.keys(merchantGroups).length > 1;

  const handleCheckout = useCallback(async () => {
    if (!username || items.length === 0) return;
    setCheckoutLoading(true);
    try {
      const result = await cartCheckout(username);
      if (result.checkouts.length > 0) {
        setCheckouts(result.checkouts);
        // If single merchant, open immediately
        if (result.checkouts.length === 1 && result.checkouts[0].checkout_url) {
          window.open(result.checkouts[0].checkout_url, "_blank");
        }
      }
    } catch (err) {
      console.error("Checkout failed:", err);
    } finally {
      setCheckoutLoading(false);
    }
  }, [username, items]);

  const openCheckoutUrl = (url: string) => {
    if (url) window.open(url, "_blank");
  };

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
            {/* Multi-merchant info banner */}
            {isMultiMerchant && (
              <div className="mb-4 flex items-start gap-2 bg-amber-950/40 border border-amber-800/50 px-4 py-3 rounded-xl">
                <Store className="h-4 w-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-amber-300">
                  You have items from {Object.keys(merchantGroups).length} stores — each requires its own checkout.
                </p>
              </div>
            )}

            {/* Items grouped by merchant */}
            <div className="flex flex-col gap-4">
              {Object.entries(merchantGroups).map(([merchantName, merchantItems]) => (
                <MerchantSection
                  key={merchantName}
                  merchantName={merchantName}
                  items={merchantItems}
                  onRemove={remove}
                />
              ))}
            </div>

            {/* Order summary */}
            <div className="mt-6 bg-zinc-900 border border-zinc-800 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-5">
                <span className="text-sm text-zinc-400">
                  {items.reduce((s, i) => s + i.quantity, 0)} item{items.reduce((s, i) => s + i.quantity, 0) !== 1 ? "s" : ""}
                  {isMultiMerchant && ` across ${Object.keys(merchantGroups).length} stores`}
                </span>
                <span className="text-lg font-bold text-zinc-100">{formatPrice(total)}</span>
              </div>

              {/* Checkout buttons */}
              <div className="flex flex-col gap-2">
                {checkouts.length > 0 ? (
                  // Show per-merchant checkout buttons after URLs are loaded
                  checkouts.map((c) => (
                    <CheckoutButton
                      key={c.merchant_name}
                      checkout={c}
                      isMulti={isMultiMerchant}
                      total={total}
                      isLoading={false}
                      onClick={openCheckoutUrl}
                    />
                  ))
                ) : (
                  // Initial state — single "Proceed" button that fetches URLs
                  <button
                    onClick={handleCheckout}
                    disabled={checkoutLoading}
                    className="w-full flex items-center justify-between bg-violet-600 hover:bg-violet-500 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold rounded-xl py-3 px-4 text-sm transition-colors shadow-lg shadow-violet-900/30"
                  >
                    <span>{checkoutLoading ? "Preparing checkout…" : "Proceed to Checkout"}</span>
                    <span className="flex items-center gap-1.5 text-violet-200">
                      {formatPrice(total)}
                      {checkoutLoading ? (
                        <div className="h-3.5 w-3.5 rounded-full border border-violet-300 border-t-transparent animate-spin" />
                      ) : (
                        <ExternalLink className="h-3.5 w-3.5" />
                      )}
                    </span>
                  </button>
                )}
              </div>

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
