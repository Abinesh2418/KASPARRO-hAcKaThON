"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { AgentName, AgentStatus, AgentStep, AgentStepData } from "@/types";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Props {
  steps: AgentStep[];
  isRunning: boolean;
  pipelineStartTime: number | null;
  pipelineEndTime: number | null;
}

// ─── Agent Config ─────────────────────────────────────────────────────────────

interface AgentConfig {
  icon: string;
  label: string;
  runningText: string;
  doneText: string;
}

const AGENT_CONFIG: Record<AgentName, AgentConfig> = {
  intent:   { icon: "🎯", label: "Understand",  runningText: "Understanding your request...", doneText: "Intent Detected"   },
  search:   { icon: "🔍", label: "Search",       runningText: "Crafting search queries...",   doneText: "Search Strategy"   },
  fetch:    { icon: "🏪", label: "Fetch",        runningText: "Searching stores...",          doneText: "Catalog Searched"  },
  compare:  { icon: "⚖",  label: "Compare",      runningText: "Scoring products...",          doneText: "Ranked & Filtered" },
  explain:  { icon: "✍",  label: "Explain",      runningText: "Writing styling notes...",     doneText: "Rationale Ready"   },
  tradeoff: { icon: "⚡",  label: "Tradeoff",     runningText: "Analyzing tradeoffs...",       doneText: "Tradeoffs Found"   },
  cart:     { icon: "🛒", label: "Cart",         runningText: "Adding to cart...",            doneText: "Added to Cart"     },
  checkout: { icon: "💳", label: "Checkout",     runningText: "Preparing checkout...",        doneText: "Checkout Ready"    },
};

const AGENT_ORDER: AgentName[] = ["intent", "search", "fetch", "compare", "explain", "tradeoff", "cart", "checkout"];

// ─── Idle ghost row ───────────────────────────────────────────────────────────

function GhostRow({ agent }: { agent: AgentName }) {
  const cfg = AGENT_CONFIG[agent];
  return (
    <div className="flex items-center gap-2 py-1.5 px-2 opacity-40">
      <span className="text-sm leading-none">{cfg.icon}</span>
      <span className="text-[11px] text-zinc-400 font-medium">{cfg.label}</span>
    </div>
  );
}

// ─── Card content renderers ───────────────────────────────────────────────────

function IntentContent({ data }: { data: AgentStepData }) {
  const color = data.constraints?.[0] ?? null;
  const budgetDisplay =
    data.budget_max != null
      ? `₹${data.budget_max.toLocaleString()}`
      : data.budget_min != null
      ? `₹${data.budget_min.toLocaleString()}+`
      : null;
  const budgetColor = data.budget_max != null || data.budget_min != null ? "text-emerald-400" : "text-amber-400";

  const rows: { label: string; value: string | null }[] = [
    { label: "Occasion",  value: data.occasion ?? null },
    { label: "Category",  value: data.product_category ?? null },
    { label: "Color",     value: color ?? null },
    { label: "Budget",    value: budgetDisplay },
    { label: "Gender",    value: data.gender ?? null },
    { label: "Recipient", value: data.recipient ?? null },
  ];

  return (
    <div className="mt-2 space-y-1.5">
      {data.intent_type && (
        <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold bg-violet-500/20 text-violet-300 border border-violet-500/30">
          {data.intent_type}
        </span>
      )}
      <div className="mt-1.5 space-y-0.5">
        {rows.map(({ label, value }) => (
          <div key={label} className="flex justify-between items-baseline gap-2">
            <span className="text-[10px] text-zinc-500 shrink-0">{label}</span>
            <span
              className={`text-[10px] font-medium truncate text-right ${
                label === "Budget" ? budgetColor : value ? "text-zinc-300" : "text-zinc-600"
              }`}
            >
              {value ?? "—"}
            </span>
          </div>
        ))}
      </div>
      {data.confidence != null && (
        <div className="flex justify-between items-baseline mt-1 pt-1 border-t border-zinc-800">
          <span className="text-[10px] text-zinc-500">Confidence</span>
          <span className="text-[10px] font-semibold text-violet-300">
            {Math.round(data.confidence * 100)}%
          </span>
        </div>
      )}
    </div>
  );
}

function SearchContent({ data }: { data: AgentStepData }) {
  const primary = data.primary_query;
  const variants = data.query_variants ?? [];
  const fallback = data.fallback_query;

  return (
    <div className="mt-2 space-y-1.5">
      {primary && (
        <div className="px-2 py-1 rounded text-[10px] text-violet-200 border border-violet-500/60 bg-violet-500/10 break-words">
          {primary}
        </div>
      )}
      {variants.map((v, i) => (
        <div
          key={i}
          className="px-2 py-1 rounded text-[10px] text-zinc-300 border border-zinc-600 bg-zinc-800/60 break-words"
        >
          {v}
        </div>
      ))}
      {fallback && (
        <div className="px-2 py-1 rounded text-[10px] text-zinc-400 border border-dashed border-zinc-600 bg-zinc-800/40 break-words">
          {fallback}
        </div>
      )}
      <p className="text-[9px] text-zinc-600 pt-0.5">primary · variant · fallback</p>
    </div>
  );
}

function FetchContent({ data }: { data: AgentStepData }) {
  const merchants = data.merchants ?? [];
  return (
    <div className="mt-2 space-y-1">
      {merchants.map((m, i) => (
        <div key={i} className="flex justify-between items-center">
          <span className="text-[10px] text-zinc-300 truncate">{m.name}</span>
          <span className="text-[10px] text-zinc-400 flex items-center gap-0.5 shrink-0">
            {m.count} <span className="text-emerald-400">✓</span>
          </span>
        </div>
      ))}
      {data.total != null && (
        <>
          <div className="border-t border-zinc-800 mt-1 pt-1" />
          <div className="flex justify-between">
            <span className="text-[10px] text-zinc-500">Total unique</span>
            <span className="text-[10px] font-semibold text-zinc-200">{data.total}</span>
          </div>
        </>
      )}
    </div>
  );
}

function CompareContent({ data }: { data: AgentStepData }) {
  const ranked = data.ranked_products ?? [];
  const maxScore = 135;

  return (
    <div className="mt-2 space-y-1">
      {ranked.map((p) => {
        const pct = Math.min(100, (p.score / maxScore) * 100);
        const isTop = p.selected;
        return (
          <div key={p.id} className={`space-y-0.5 ${isTop ? "opacity-100" : "opacity-30"}`}>
            <div className="flex justify-between items-baseline gap-1">
              <span className="text-[10px] text-zinc-300 truncate">
                {isTop && <span className="text-amber-400 mr-0.5">★</span>}
                {p.title}
              </span>
              <span className="text-[9px] font-mono text-zinc-400 shrink-0">{p.score}</span>
            </div>
            <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${isTop ? "bg-violet-500" : "bg-zinc-600"}`}
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </div>
          </div>
        );
      })}
      {data.total_candidates != null && data.finalists_count != null && (
        <p className="text-[10px] text-zinc-500 pt-1">
          {data.total_candidates} → <span className="text-violet-300 font-semibold">{data.finalists_count} finalists</span>
        </p>
      )}
    </div>
  );
}

function ExplainContent({ data }: { data: AgentStepData }) {
  const explanations = (data.explanations ?? []).slice(0, 3);
  return (
    <div className="mt-2 space-y-2">
      {explanations.map((e, i) => (
        <motion.div
          key={e.product_id}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25, delay: i * 0.2 }}
          className="bg-zinc-800/60 rounded p-2 relative"
        >
          <span className="absolute top-1 right-2 text-2xl leading-none text-zinc-700 select-none font-serif">"</span>
          <p className="text-[10px] font-semibold text-zinc-200 pr-4 truncate">{e.title}</p>
          <p className="text-[10px] text-zinc-400 mt-0.5 leading-relaxed line-clamp-3">{e.rationale}</p>
        </motion.div>
      ))}
    </div>
  );
}

function TradeoffContent({ data }: { data: AgentStepData }) {
  const panels = data.panels ?? [];
  if (panels.length === 0) {
    return (
      <p className="mt-2 text-[10px] text-zinc-500 italic">
        No tensions detected — products are comparable
      </p>
    );
  }
  return (
    <div className="mt-2 space-y-2">
      {panels.map((p) => (
        <div key={p.id} className="border border-zinc-700/60 rounded p-2 bg-zinc-800/40">
          <p className="text-[10px] font-semibold text-zinc-200 truncate">{p.title}</p>
          <p className="text-[10px] text-emerald-400 mt-0.5">{p.highlight}</p>
          <p className="text-[10px] text-amber-400 mt-0.5">{p.tradeoff}</p>
        </div>
      ))}
    </div>
  );
}

function CartContent({ data }: { data: AgentStepData }) {
  const added = data.added ?? [];
  return (
    <div className="mt-2 space-y-1">
      {added.map((item, i) => (
        <div key={i} className="flex justify-between items-start gap-1">
          <div className="flex flex-col min-w-0">
            <span className="text-[10px] text-zinc-300 truncate">{item.title}</span>
            <span className="text-[9px] text-zinc-500">{item.merchant}</span>
          </div>
          <span className="text-[10px] font-semibold text-zinc-200 shrink-0">
            ₹{item.price.toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  );
}

function CheckoutContent({ data }: { data: AgentStepData }) {
  const merchants = data.checkout_merchants ?? [];
  return (
    <div className="mt-2 space-y-1">
      {merchants.map((m, i) => (
        <div key={i} className="flex justify-between items-baseline">
          <div className="flex flex-col min-w-0">
            <span className="text-[10px] text-zinc-300 truncate">{m.name}</span>
            <span className="text-[9px] text-zinc-500">{m.item_count} item{m.item_count !== 1 ? "s" : ""}</span>
          </div>
          <span className="text-[10px] text-zinc-300 shrink-0">₹{m.subtotal.toLocaleString()}</span>
        </div>
      ))}
      {data.grand_total != null && (
        <>
          <div className="border-t border-zinc-700 mt-1 pt-1" />
          <div className="flex justify-between">
            <span className="text-[10px] font-semibold text-zinc-300">Grand Total</span>
            <span className="text-[10px] font-bold text-emerald-400">₹{data.grand_total.toLocaleString()}</span>
          </div>
        </>
      )}
    </div>
  );
}

function CardContent({ agent, data }: { agent: AgentName; data: AgentStepData }) {
  switch (agent) {
    case "intent":   return <IntentContent data={data} />;
    case "search":   return <SearchContent data={data} />;
    case "fetch":    return <FetchContent data={data} />;
    case "compare":  return <CompareContent data={data} />;
    case "explain":  return <ExplainContent data={data} />;
    case "tradeoff": return <TradeoffContent data={data} />;
    case "cart":     return <CartContent data={data} />;
    case "checkout": return <CheckoutContent data={data} />;
    default:         return null;
  }
}

// ─── Spinner ──────────────────────────────────────────────────────────────────

function Spinner() {
  return (
    <motion.span
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      className="inline-block text-[11px] leading-none"
    >
      ◌
    </motion.span>
  );
}

// ─── Single agent card ────────────────────────────────────────────────────────

function AgentCard({ step, index }: { step: AgentStep; index: number }) {
  const cfg = AGENT_CONFIG[step.agent];
  const { status, data } = step;

  // skipped: slim row
  if (status === "skipped") {
    return (
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 0.4, y: 0 }}
        transition={{ duration: 0.2, delay: index * 0.04 }}
        className="flex items-center gap-2 px-2 py-1.5 rounded border border-zinc-800/60"
      >
        <span className="text-sm leading-none opacity-60">{cfg.icon}</span>
        <span className="text-[11px] text-zinc-500 flex-1">{cfg.label}</span>
        <span className="text-[10px] text-zinc-600 font-mono">–</span>
      </motion.div>
    );
  }

  // waiting: dashed, dim
  if (status === "waiting") {
    return (
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 0.3, y: 0 }}
        transition={{ duration: 0.2, delay: index * 0.04 }}
        className="flex items-center gap-2 px-2 py-1.5 rounded border border-dashed border-zinc-700/60"
      >
        <span className="text-sm leading-none">{cfg.icon}</span>
        <span className="text-[11px] text-zinc-500">{cfg.label}</span>
      </motion.div>
    );
  }

  // running
  if (status === "running") {
    return (
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, delay: index * 0.04 }}
        className="px-2 py-2 rounded border border-violet-500/70 bg-violet-950/20"
        style={{ boxShadow: "0 0 8px rgba(139,92,246,0.25)" }}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm leading-none">{cfg.icon}</span>
          <span className="text-[11px] text-violet-300 font-semibold flex-1">Running...</span>
          <Spinner />
        </div>
        <p className="text-[10px] text-violet-400/70 mt-0.5 pl-5">{cfg.runningText}</p>
      </motion.div>
    );
  }

  // complete
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.04 }}
      className="px-2 py-2 rounded border border-zinc-700/60 bg-zinc-900/60"
    >
      <div className="flex items-center gap-2">
        <span className="text-sm leading-none">{cfg.icon}</span>
        <span className="text-[11px] text-zinc-200 font-semibold flex-1">{cfg.doneText}</span>
        <span className="text-[10px] text-emerald-400 font-bold">✓</span>
      </div>
      {data && (
        <div className="pl-0">
          <CardContent agent={step.agent} data={data} />
        </div>
      )}
    </motion.div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export function AgentPanel({ steps, isRunning, pipelineStartTime, pipelineEndTime }: Props) {
  const isDone = !isRunning && steps.length > 0;
  const duration =
    isDone && pipelineStartTime != null && pipelineEndTime != null
      ? ((pipelineEndTime - pipelineStartTime) / 1000).toFixed(1)
      : null;

  // Build a lookup for quick access
  const stepMap = new Map<AgentName, AgentStep>(steps.map((s) => [s.agent, s]));

  return (
    <div className="flex flex-col h-full bg-zinc-950 select-none">
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-b border-zinc-800/60 shrink-0">
        <span className="text-xs text-zinc-200 font-semibold tracking-wide">✦ Curio&apos;s Brain</span>
        {isRunning && (
          <span className="ml-auto text-[10px] text-violet-400 flex items-center gap-1">
            <motion.span
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
            >
              ●
            </motion.span>
            live
          </span>
        )}
      </div>

      {/* Idle state */}
      {steps.length === 0 && (
        <div className="flex flex-col flex-1 px-2 pt-2 pb-3">
          <div className="space-y-0.5">
            {AGENT_ORDER.map((agent) => (
              <GhostRow key={agent} agent={agent} />
            ))}
          </div>
          <p className="mt-4 px-1 text-[10px] text-zinc-600 leading-relaxed">
            Type a shopping query to see the pipeline in action
          </p>
        </div>
      )}

      {/* Active state */}
      {steps.length > 0 && (
        <div className="flex flex-col flex-1 min-h-0">
          <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1.5">
            <AnimatePresence initial={false}>
              {AGENT_ORDER.map((agentName, i) => {
                const step = stepMap.get(agentName);
                if (!step) return null;
                return <AgentCard key={agentName} step={step} index={i} />;
              })}
            </AnimatePresence>
          </div>

          {/* Footer: completed */}
          {isDone && duration != null && (
            <motion.div
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="shrink-0 px-3 py-2 border-t border-zinc-800/60 flex items-center justify-between"
            >
              <span className="text-[10px] text-zinc-500">
                Completed in{" "}
                <span className="text-zinc-300 font-semibold">{duration}s</span>
                <span className="text-zinc-600"> · 8 agents</span>
              </span>
              <span className="text-[10px] text-emerald-400">✓</span>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
