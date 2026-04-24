"use client";

import { Sliders, Palette, Tag, DollarSign, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Preferences } from "@/types";

interface Props {
  preferences: Preferences;
  className?: string;
}

function Section({
  icon: Icon,
  label,
  children,
}: {
  icon: React.ElementType;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-zinc-400 uppercase tracking-wider">
        <Icon className="h-3.5 w-3.5" />
        {label}
      </div>
      {children}
    </div>
  );
}

function TagChip({ label, color = "zinc" }: { label: string; color?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium transition-all animate-in fade-in",
        color === "violet"
          ? "bg-violet-900/40 text-violet-300 border border-violet-700/50"
          : "bg-zinc-800 text-zinc-300 border border-zinc-700/50"
      )}
    >
      {label}
    </span>
  );
}

function Empty() {
  return <span className="text-xs text-zinc-600 italic">Learning from conversation…</span>;
}

export function PreferencePanel({ preferences, className }: Props) {
  const hasAny = [
    preferences.style,
    preferences.colors,
    preferences.sizes,
    preferences.occasions,
  ].some((arr) => arr.length > 0) || preferences.budget_max;

  return (
    <aside
      className={cn(
        "flex flex-col gap-5 rounded-2xl border border-zinc-800 bg-zinc-900/80 p-5 backdrop-blur-sm",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="h-7 w-7 rounded-full bg-violet-900/50 border border-violet-700/40 flex items-center justify-center">
          <Sliders className="h-3.5 w-3.5 text-violet-400" />
        </div>
        <div>
          <p className="text-sm font-semibold text-zinc-100">Your Style Profile</p>
          <p className="text-[10px] text-zinc-500">Updated as we chat</p>
        </div>
      </div>

      {!hasAny && (
        <div className="rounded-xl border border-dashed border-zinc-700 p-4 text-center">
          <p className="text-xs text-zinc-500">
            Start chatting and I'll learn your style, budget, and preferences in real-time.
          </p>
        </div>
      )}

      {/* Style */}
      {preferences.style.length > 0 && (
        <Section icon={Tag} label="Style">
          <div className="flex flex-wrap gap-1.5">
            {preferences.style.map((s) => (
              <TagChip key={s} label={s} color="violet" />
            ))}
          </div>
        </Section>
      )}

      {/* Colors */}
      {preferences.colors.length > 0 && (
        <Section icon={Palette} label="Colors">
          <div className="flex flex-wrap gap-1.5">
            {preferences.colors.map((c) => (
              <TagChip key={c} label={c} />
            ))}
          </div>
        </Section>
      )}

      {/* Sizes */}
      {preferences.sizes.length > 0 && (
        <Section icon={Sliders} label="Sizes">
          <div className="flex flex-wrap gap-1.5">
            {preferences.sizes.map((s) => (
              <TagChip key={s} label={s.toUpperCase()} />
            ))}
          </div>
        </Section>
      )}

      {/* Budget */}
      {preferences.budget_max && (
        <Section icon={DollarSign} label="Budget">
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-violet-600 to-purple-500"
                style={{ width: `${Math.min((preferences.budget_max / 500) * 100, 100)}%` }}
              />
            </div>
            <span className="text-xs font-medium text-zinc-300">
              under ${preferences.budget_max}
            </span>
          </div>
        </Section>
      )}

      {/* Occasions */}
      {preferences.occasions.length > 0 && (
        <Section icon={Calendar} label="Occasions">
          <div className="flex flex-wrap gap-1.5">
            {preferences.occasions.map((o) => (
              <TagChip key={o} label={o} />
            ))}
          </div>
        </Section>
      )}

      {/* Footer */}
      <div className="mt-auto pt-3 border-t border-zinc-800">
        <p className="text-[10px] text-zinc-600 text-center leading-relaxed">
          Powered by Curio AI
        </p>
      </div>
    </aside>
  );
}
