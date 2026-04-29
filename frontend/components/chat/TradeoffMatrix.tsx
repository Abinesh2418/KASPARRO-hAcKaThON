"use client";

import { motion } from "framer-motion";
import type { TradeoffData, ScoredProduct, TradeoffPanel } from "@/types";

const DIMENSIONS = [
  { key: "occasion_fit",      label: "Occasion Fit",  max: 30 },
  { key: "style_match",       label: "Style Match",   max: 25 },
  { key: "budget_fit",        label: "Budget Fit",    max: 25 },
  { key: "category_match",    label: "Category",      max: 20 },
  { key: "color_match",       label: "Color",         max: 15 },
  { key: "stock_availability",label: "Availability",  max: 10 },
  { key: "value_score",       label: "Value",         max: 10 },
] as const;

function ScoreBar({ value, max, delay }: { value: number; max: number; delay: number }) {
  const pct = Math.min(100, (value / max) * 100);
  const gradient =
    pct >= 75
      ? "from-emerald-500 to-emerald-400"
      : pct >= 45
      ? "from-amber-500 to-yellow-400"
      : "from-red-600 to-red-400";

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-zinc-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${gradient}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, delay, ease: "easeOut" }}
        />
      </div>
      <span className="text-[10px] font-mono text-zinc-400 w-9 text-right tabular-nums">
        {value}<span className="text-zinc-600">/{max}</span>
      </span>
    </div>
  );
}

function ScoringTable({ products }: { products: ScoredProduct[] }) {
  const top = products.slice(0, 3);
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr>
            <th className="text-left pb-3 pr-4 text-zinc-600 font-medium text-[11px] uppercase tracking-wider w-24">
              Dimension
            </th>
            {top.map((p, i) => (
              <th key={p.product_id} className="pb-3 px-3 text-center">
                <div className="flex flex-col items-center gap-1">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    i === 0 ? "bg-violet-600/20 text-violet-300" :
                    i === 1 ? "bg-blue-600/20 text-blue-300" :
                    "bg-zinc-700/40 text-zinc-400"
                  }`}>P{i + 1}</span>
                  <span className="text-zinc-300 font-medium text-[11px] leading-tight text-center max-w-[90px]">
                    {p.title.split(" ").slice(0, 3).join(" ")}
                  </span>
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {DIMENSIONS.map((dim, i) => (
            <motion.tr
              key={dim.key}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06, duration: 0.25 }}
              className="border-t border-zinc-800/60"
            >
              <td className="py-2 pr-4 text-zinc-500 text-[11px] whitespace-nowrap">
                {dim.label}
              </td>
              {top.map((p, pi) => {
                const val = p.dimension_scores[dim.key as keyof typeof p.dimension_scores];
                return (
                  <td key={p.product_id} className="py-2 px-3 min-w-[110px]">
                    <ScoreBar value={val} max={dim.max} delay={i * 0.06 + pi * 0.03} />
                  </td>
                );
              })}
            </motion.tr>
          ))}
          {/* Total row */}
          <tr className="border-t-2 border-zinc-700">
            <td className="pt-3 pr-4 text-zinc-300 font-bold text-[11px] uppercase tracking-wider">
              Total
            </td>
            {top.map((p, i) => (
              <td key={p.product_id} className="pt-3 px-3 text-center">
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5 + i * 0.08 }}
                  className="inline-flex flex-col items-center"
                >
                  <span className={`text-lg font-black ${
                    i === 0 ? "text-violet-400" : i === 1 ? "text-blue-400" : "text-zinc-400"
                  }`}>{p.score}</span>
                  <span className="text-[9px] text-zinc-600">/135</span>
                </motion.div>
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

interface TradeoffPanelCardProps {
  panel: TradeoffPanel;
  productTitle: string;
  onSendMessage: (msg: string) => void;
}

function TradeoffPanelCard({ panel, productTitle, onSendMessage }: TradeoffPanelCardProps) {
  const isBestFit = panel.id === "best_fit";
  const shortName = productTitle.split(" ").slice(0, 4).join(" ");

  const getButtonLabel = (reply: string) => {
    if (reply === "Add to cart") return `Add ${panel.title} — ${shortName}`;
    return reply;
  };

  const getButtonMessage = (reply: string) => {
    if (reply === "Add to cart") return `Add ${productTitle} to cart`;
    return reply;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className={`flex-1 min-w-0 rounded-xl border p-3 space-y-2 ${
        isBestFit
          ? "border-violet-500/30 bg-violet-950/20"
          : "border-emerald-700/30 bg-emerald-950/15"
      }`}
    >
      <span className={`inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${
        isBestFit ? "bg-violet-600/25 text-violet-300" : "bg-emerald-700/25 text-emerald-300"
      }`}>
        {isBestFit ? "🎯" : "💰"} {panel.title}
      </span>

      <p className="text-xs text-zinc-200 font-medium leading-snug">{panel.highlight}</p>
      <p className="text-[11px] text-zinc-500 leading-snug">
        <span className="text-zinc-400 font-medium">Trade-off: </span>{panel.tradeoff}
      </p>

      <div className="flex flex-wrap gap-1.5 pt-0.5">
        {panel.quick_replies.map((reply) => (
          <button
            key={reply}
            onClick={() => onSendMessage(getButtonMessage(reply))}
            className={`text-[11px] px-2.5 py-1 rounded-lg border transition-colors ${
              reply === "Add to cart"
                ? isBestFit
                  ? "bg-violet-600/20 hover:bg-violet-600/40 text-violet-300 border-violet-500/30 hover:border-violet-400/50"
                  : "bg-emerald-700/20 hover:bg-emerald-700/40 text-emerald-300 border-emerald-600/30 hover:border-emerald-500/50"
                : "bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-zinc-100 border-zinc-700 hover:border-zinc-600"
            }`}
          >
            {getButtonLabel(reply)}
          </button>
        ))}
      </div>
    </motion.div>
  );
}

interface Props {
  tradeoffData: TradeoffData;
  onSendMessage: (msg: string) => void;
}

export function TradeoffMatrix({ tradeoffData, onSendMessage }: Props) {
  const { scored_products, tradeoff_panels } = tradeoffData;
  if (!scored_products?.length) return null;
  const showPanels = tradeoff_panels?.length >= 2;

  const getProductTitle = (productId: string) =>
    scored_products.find((p) => p.product_id === productId)?.title ?? "this item";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mt-3 space-y-2"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-1">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />
        <span className="text-[11px] font-bold uppercase tracking-widest text-violet-400 flex items-center gap-1.5">
          <span>⬡</span> Visual Tradeoff Matrix
        </span>
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />
      </div>

      {/* Scoring table */}
      <div className="bg-zinc-900/60 border border-zinc-700/40 rounded-xl p-3.5 backdrop-blur-sm">
        <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-3">
          Score Breakdown
        </p>
        <ScoringTable products={scored_products} />
      </div>

      {/* Tradeoff panels */}
      {showPanels && (
        <div className="flex gap-2">
          {tradeoff_panels.map((panel) => (
            <TradeoffPanelCard
              key={panel.id}
              panel={panel}
              productTitle={getProductTitle(panel.product_id)}
              onSendMessage={onSendMessage}
            />
          ))}
        </div>
      )}
    </motion.div>
  );
}
