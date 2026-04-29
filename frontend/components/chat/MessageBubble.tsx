"use client";

import ReactMarkdown from "react-markdown";
import { useState, useEffect } from "react";
import { ShoppingBag, ExternalLink, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Message, MerchantCheckout } from "@/types";
import { InlineProducts } from "@/components/products/InlineProducts";
import { TypingIndicator } from "./TypingIndicator";
import { TradeoffMatrix } from "./TradeoffMatrix";

interface Props {
  message: Message;
  onSendMessage?: (msg: string) => void;
}

function CheckoutCard({ checkouts, grandTotal, totalItems, isMultiMerchant }: {
  checkouts: MerchantCheckout[];
  grandTotal: number;
  totalItems: number;
  isMultiMerchant: boolean;
}) {
  const [initiated, setInitiated] = useState<Set<string>>(new Set());
  const [paid, setPaid] = useState<Set<string>>(new Set());

  useEffect(() => {
    const onFocus = () => {
      if (initiated.size > 0) {
        setPaid(prev => new Set([...prev, ...initiated]));
        setInitiated(new Set());
      }
    };
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [initiated]);

  const handleCheckout = (merchantName: string, url: string | null) => {
    if (!url) return;
    window.open(url, "_blank");
    setInitiated(prev => new Set([...prev, merchantName]));
  };

  return (
    <div className="space-y-3 mt-4">
      {/* Cart summary card */}
      <div className="bg-zinc-900 border border-zinc-700 rounded-xl overflow-hidden shadow-lg">
        {/* Header */}
        <div className="px-4 py-3 border-b border-zinc-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingBag className="h-4 w-4 text-violet-400" />
            <span className="font-semibold text-sm text-zinc-100">Your cart</span>
          </div>
          <span className="text-xs text-zinc-400">
            {totalItems} item{totalItems !== 1 ? "s" : ""} · ${grandTotal.toLocaleString()}
          </span>
        </div>

        {/* Items grouped by merchant */}
        <div className="divide-y divide-zinc-800">
          {checkouts.map((merchant) => (
            <div key={merchant.merchant_name} className="p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-zinc-400">
                  🏪 {merchant.merchant_name}
                </span>
                <span className="text-xs text-zinc-500">
                  {merchant.item_count} item{merchant.item_count !== 1 ? "s" : ""} · ${merchant.subtotal.toLocaleString()}
                </span>
              </div>

              <div className="space-y-3">
                {merchant.items.map((item, idx) => (
                  <div key={idx} className="flex gap-3 items-center">
                    <img
                      src={item.image}
                      alt={item.title}
                      className="w-12 h-12 rounded-lg object-cover flex-shrink-0 border border-zinc-700"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-zinc-100 truncate">{item.title}</p>
                      <p className="text-xs text-zinc-500">
                        Size {item.size}{item.color ? ` · ${item.color}` : ""} · Qty {item.quantity}
                      </p>
                    </div>
                    <span className="text-sm font-medium text-zinc-200 whitespace-nowrap">
                      ${item.subtotal_for_line.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Total footer */}
        <div className="px-4 py-3 bg-zinc-800/50 flex justify-between items-center border-t border-zinc-700">
          <span className="font-semibold text-sm text-zinc-300">Total</span>
          <span className="font-bold text-lg text-zinc-100">
            ${grandTotal.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Multi-merchant info banner */}
      {isMultiMerchant && (
        <div className="bg-amber-950/40 border border-amber-800/50 px-3 py-2 rounded-lg">
          <p className="text-xs text-amber-300">
            🏬 {checkouts.length} stores — each has its own checkout
          </p>
        </div>
      )}

      {/* Checkout buttons — one per merchant */}
      {checkouts.map((c) => {
        const isDone = paid.has(c.merchant_name);
        return isDone ? (
          <div key={c.merchant_name} className="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white text-sm font-medium flex items-center justify-between">
            <span className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Paid — {c.merchant_name}
            </span>
            <span>${c.subtotal.toLocaleString()}</span>
          </div>
        ) : (
          <button
            key={c.merchant_name}
            onClick={() => handleCheckout(c.merchant_name, c.checkout_url)}
            disabled={!c.checkout_url}
            className="w-full px-4 py-3 rounded-xl font-medium text-sm flex items-center justify-between bg-violet-600 hover:bg-violet-700 disabled:opacity-40 disabled:cursor-not-allowed text-white transition-colors"
          >
            <span>{isMultiMerchant ? `Step ${c.step} of ${checkouts.length} — ` : ""}Checkout with {c.merchant_name}</span>
            <span className="flex items-center gap-2 opacity-90">
              ${c.subtotal.toLocaleString()}
              <ExternalLink className="h-3 w-3" />
            </span>
          </button>
        );
      })}
    </div>
  );
}

export function MessageBubble({ message, onSendMessage }: Props) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[75%] space-y-1.5">
          {message.imageUrl && (
            <div className="flex justify-end">
              <img
                src={message.imageUrl}
                alt="Uploaded"
                className="max-h-40 rounded-xl object-cover border border-violet-500/30 shadow-md"
              />
            </div>
          )}
          {message.content && (
            <div className="rounded-2xl rounded-tr-sm bg-violet-600 px-4 py-3 text-sm text-white shadow-lg shadow-violet-900/20">
              {message.content}
            </div>
          )}
        </div>
      </div>
    );
  }

  const checkout = message.metadata;

  return (
    <div className="flex flex-col gap-3 mb-4">
      <div className="flex items-start gap-3">
        {/* Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-xs font-bold text-white shadow-md">
          C
        </div>

        <div className="flex-1 min-w-0">
          {/* Message content */}
          <div
            className={cn(
              "rounded-2xl rounded-tl-sm px-4 py-3 text-sm shadow-sm",
              message.isError
                ? "bg-red-950/50 border border-red-800 text-red-300"
                : "bg-zinc-800/80 border border-zinc-700/50 text-zinc-100"
            )}
          >
            {message.isStreaming && !message.content ? (
              <TypingIndicator />
            ) : (
              <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-p:my-1">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
            {message.isStreaming && message.content && (
              <span className="inline-block w-0.5 h-4 bg-violet-400 animate-pulse ml-0.5 align-middle" />
            )}
          </div>

          {/* Checkout cart card */}
          {checkout?.show_cart_summary && checkout.checkouts?.length > 0 && (
            <CheckoutCard
              checkouts={checkout.checkouts}
              grandTotal={checkout.grand_total}
              totalItems={checkout.total_items}
              isMultiMerchant={checkout.is_multi_merchant}
            />
          )}

          {/* Tradeoff matrix */}
          {message.tradeoffData && !message.isStreaming && onSendMessage && (
            <TradeoffMatrix
              tradeoffData={message.tradeoffData}
              onSendMessage={onSendMessage}
            />
          )}
        </div>
      </div>

      {/* Inline product recommendations */}
      {message.products && message.products.length > 0 && (
        <div className="ml-11">
          <InlineProducts products={message.products} />
        </div>
      )}
    </div>
  );
}
