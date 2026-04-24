"use client";

import { Sparkles } from "lucide-react";
import type { VisualSearchResult } from "@/types";

interface Props {
  result: VisualSearchResult;
}

export function AttributeTags({ result }: Props) {
  const { attributes } = result;

  return (
    <div className="rounded-xl border border-violet-700/30 bg-violet-900/10 p-4 space-y-3 animate-in fade-in duration-500">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-violet-400" />
        <p className="text-sm font-semibold text-violet-300">Style detected from your image</p>
      </div>

      <p className="text-xs text-zinc-400 italic">{attributes.description}</p>

      <div className="flex flex-wrap gap-1.5">
        {attributes.style?.map((s: string) => (
          <span
            key={s}
            className="px-2.5 py-1 rounded-full text-xs bg-violet-800/40 text-violet-200 border border-violet-700/40"
          >
            {s}
          </span>
        ))}
        {attributes.colors?.map((c: string) => (
          <span
            key={c}
            className="px-2.5 py-1 rounded-full text-xs bg-zinc-800 text-zinc-300 border border-zinc-700"
          >
            {c}
          </span>
        ))}
        {attributes.silhouette && (
          <span className="px-2.5 py-1 rounded-full text-xs bg-zinc-800 text-zinc-300 border border-zinc-700">
            {attributes.silhouette}
          </span>
        )}
        {attributes.occasion?.map((o: string) => (
          <span
            key={o}
            className="px-2.5 py-1 rounded-full text-xs bg-emerald-900/30 text-emerald-300 border border-emerald-700/40"
          >
            {o}
          </span>
        ))}
      </div>
    </div>
  );
}
