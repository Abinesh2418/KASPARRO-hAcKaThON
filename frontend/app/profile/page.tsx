"use client";

import Link from "next/link";
import { Sparkles, Tag, Palette, Ruler, DollarSign, Calendar, ArrowRight, MessageCircle } from "lucide-react";

const SAMPLE_STYLES = ["minimal", "chic", "classic"];
const SAMPLE_COLORS = ["black", "cream", "sage", "camel"];
const SAMPLE_OCCASIONS = ["office", "casual", "date night"];

export default function ProfilePage() {
  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-2xl mx-auto px-6 lg:px-10 py-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-10">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center shadow-xl shadow-violet-900/40">
            <Sparkles className="h-7 w-7 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-zinc-100">Style Profile</h1>
            <p className="text-sm text-zinc-500 mt-0.5">Built by Curio from your conversations</p>
          </div>
        </div>

        {/* Profile card */}
        <div className="space-y-4">
          {/* Style */}
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Tag className="h-4 w-4 text-violet-400" />
              <span className="text-sm font-semibold text-zinc-200">Your Style</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_STYLES.map((s) => (
                <span key={s} className="capitalize px-3 py-1 rounded-full bg-violet-900/30 border border-violet-500/30 text-violet-300 text-xs font-medium">
                  {s}
                </span>
              ))}
            </div>
          </div>

          {/* Colors */}
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Palette className="h-4 w-4 text-violet-400" />
              <span className="text-sm font-semibold text-zinc-200">Preferred Colors</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_COLORS.map((c) => (
                <span key={c} className="capitalize px-3 py-1 rounded-full bg-zinc-800 border border-zinc-700/60 text-zinc-300 text-xs font-medium">
                  {c}
                </span>
              ))}
            </div>
          </div>

          {/* Size + Budget */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Ruler className="h-4 w-4 text-violet-400" />
                <span className="text-sm font-semibold text-zinc-200">Size</span>
              </div>
              <span className="text-2xl font-black text-zinc-100">M</span>
            </div>
            <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <DollarSign className="h-4 w-4 text-violet-400" />
                <span className="text-sm font-semibold text-zinc-200">Budget</span>
              </div>
              <span className="text-2xl font-black text-zinc-100">$150</span>
              <p className="text-[10px] text-zinc-500 mt-1">max per item</p>
            </div>
          </div>

          {/* Occasions */}
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Calendar className="h-4 w-4 text-violet-400" />
              <span className="text-sm font-semibold text-zinc-200">Occasions</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_OCCASIONS.map((o) => (
                <span key={o} className="capitalize px-3 py-1 rounded-full bg-zinc-800 border border-zinc-700/60 text-zinc-300 text-xs font-medium">
                  {o}
                </span>
              ))}
            </div>
          </div>

          {/* CTA */}
          <div className="bg-gradient-to-br from-violet-950/60 to-purple-950/40 border border-violet-700/30 rounded-2xl p-6 text-center">
            <MessageCircle className="h-8 w-8 text-violet-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-zinc-200 mb-1">Make it yours</p>
            <p className="text-xs text-zinc-500 mb-4">Chat with Curio to refine your style profile and get better recommendations</p>
            <Link
              href="/curio"
              className="inline-flex items-center gap-2 bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium px-4 py-2 rounded-xl transition-all"
            >
              Open Curio <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
