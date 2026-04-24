"use client";

import { useState, useCallback } from "react";
import { useChat } from "@/hooks/use-chat";
import { visualSearch } from "@/services/api";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { PreferencePanel } from "@/components/preferences/PreferencePanel";
import { InlineProducts } from "@/components/products/InlineProducts";
import { Sliders, X } from "lucide-react";
import type { VisualSearchResult } from "@/types";
import { cn } from "@/lib/utils";

export function ChatInterface() {
  const { state, sendMessage, bottomRef } = useChat();
  const [showPrefs, setShowPrefs] = useState(false);
  const [visualResult, setVisualResult] = useState<VisualSearchResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleImageUpload = useCallback(async (file: File) => {
    setIsSearching(true);
    setVisualResult(null);
    try {
      const result = await visualSearch(file);
      setVisualResult(result);
    } catch (err) {
      console.error("Visual search failed:", err);
    } finally {
      setIsSearching(false);
    }
  }, []);

  return (
    <div className="flex h-full w-full bg-zinc-950 overflow-hidden">
      {/* ── Preference Sidebar (desktop) ── */}
      <aside className="hidden lg:flex flex-col w-72 xl:w-80 flex-shrink-0 border-r border-zinc-800/60 overflow-y-auto p-4">
        <PreferencePanel preferences={state.preferences} className="flex-1" />
      </aside>

      {/* ── Main chat area ── */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/60 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-900/30">
              <span className="text-sm font-black text-white">S</span>
            </div>
            <div>
              <h1 className="text-sm font-bold text-zinc-100 leading-none">Shopify</h1>
              <p className="text-[10px] text-zinc-500 mt-0.5">AI Fashion Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Online indicator */}
            <div className="flex items-center gap-1.5 bg-emerald-900/30 border border-emerald-700/40 rounded-full px-2.5 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] text-emerald-400 font-medium">Live</span>
            </div>

            {/* Mobile prefs toggle */}
            <button
              onClick={() => setShowPrefs(true)}
              className="lg:hidden p-2 rounded-xl text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
            >
              <Sliders className="h-4 w-4" />
            </button>
          </div>
        </header>

        {/* Visual search result banner */}
        {(isSearching || visualResult) && (
          <div className="px-4 pt-4 flex-shrink-0">
            {isSearching ? (
              <div className="rounded-xl border border-zinc-700/50 bg-zinc-800/50 p-4 flex items-center gap-3">
                <div className="h-4 w-4 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
                <span className="text-sm text-zinc-400">Analyzing your image with Gemma4…</span>
              </div>
            ) : visualResult ? (
              <div className="space-y-3">
                <div className="flex items-center justify-end">
                  <button
                    onClick={() => setVisualResult(null)}
                    className="p-1.5 rounded-lg text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
                {visualResult.products.length > 0 && (
                  <InlineProducts
                    products={visualResult.products}
                    title="Similar items found"
                  />
                )}
              </div>
            ) : null}
          </div>
        )}

        {/* Error banner */}
        {state.error && (
          <div className="mx-4 mt-4 flex-shrink-0 rounded-xl border border-red-800/50 bg-red-950/30 px-4 py-3 text-xs text-red-400">
            {state.error}
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          <MessageList messages={state.messages} bottomRef={bottomRef} />
        </div>

        {/* Input */}
        <div className="flex-shrink-0">
          <ChatInput
            onSend={sendMessage}
            onImageUpload={handleImageUpload}
            isStreaming={state.isStreaming}
          />
        </div>
      </div>

      {/* ── Mobile preference drawer ── */}
      {showPrefs && (
        <div className="lg:hidden fixed inset-0 z-50 flex flex-col justify-end">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowPrefs(false)}
          />
          <div className="relative z-10 max-h-[80vh] overflow-y-auto rounded-t-3xl border-t border-zinc-700 bg-zinc-900 p-5">
            <div className="flex items-center justify-between mb-4">
              <p className="font-semibold text-zinc-100">Your Style Profile</p>
              <button
                onClick={() => setShowPrefs(false)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <PreferencePanel preferences={state.preferences} />
          </div>
        </div>
      )}
    </div>
  );
}
