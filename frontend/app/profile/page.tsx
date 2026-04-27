"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Tag, Palette, Ruler, IndianRupee, Calendar, ArrowRight, MessageCircle, User } from "lucide-react";
import type { Preferences } from "@/types";

const EMPTY_PREFS: Preferences = {
  style: [],
  colors: [],
  sizes: [],
  budget_max: null,
  budget_min: null,
  occasions: [],
};

const DEMO_PREFS: Preferences = {
  style: ["minimal", "classic", "formal"],
  colors: ["black", "white", "silver"],
  sizes: ["M"],
  budget_max: 5000,
  budget_min: null,
  occasions: ["office", "casual", "formal"],
};

function EmptyBadge({ label }: { label: string }) {
  return (
    <span className="px-3 py-1 rounded-full bg-zinc-800/50 border border-zinc-700/40 text-zinc-600 text-xs italic">
      {label}
    </span>
  );
}

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<{ username: string; name: string } | null>(null);
  const [prefs, setPrefs] = useState<Preferences>(EMPTY_PREFS);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const rawUser = localStorage.getItem("curio_user");
      if (!rawUser) { router.push("/login"); return; }
      const parsedUser = JSON.parse(rawUser);
      setUser(parsedUser);

      const rawChat = localStorage.getItem("curio-chat-state");
      let loadedPrefs: Preferences | null = null;
      if (rawChat) {
        const chatState = JSON.parse(rawChat);
        if (chatState.preferences) loadedPrefs = chatState.preferences;
      }

      const hasPrefs =
        loadedPrefs &&
        (loadedPrefs.style.length > 0 ||
          loadedPrefs.colors.length > 0 ||
          loadedPrefs.occasions.length > 0 ||
          loadedPrefs.budget_max !== null ||
          loadedPrefs.sizes.length > 0);

      // Show demo defaults for demo user when no real preferences exist yet
      if (!hasPrefs && parsedUser?.username === "demo") {
        setPrefs(DEMO_PREFS);
      } else if (loadedPrefs) {
        setPrefs(loadedPrefs);
      }
    } catch {}
    setLoaded(true);
  }, [router]);

  if (!loaded) {
    return (
      <div className="h-full flex items-center justify-center bg-zinc-950">
        <div className="h-6 w-6 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  const initials = user?.name
    ? user.name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2)
    : "?";

  const hasAnyPrefs =
    prefs.style.length > 0 ||
    prefs.colors.length > 0 ||
    prefs.occasions.length > 0 ||
    prefs.budget_max !== null ||
    prefs.sizes.length > 0;

  return (
    <div className="h-full overflow-y-auto bg-zinc-950">
      <div className="max-w-2xl mx-auto px-6 lg:px-10 py-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-10">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center shadow-xl shadow-violet-900/40 flex-shrink-0">
            <span className="text-xl font-black text-white">{initials}</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-zinc-100">{user?.name ?? "Your Profile"}</h1>
            <p className="text-sm text-zinc-500 mt-0.5">
              {hasAnyPrefs
                ? "Style profile built by Curio from your conversations"
                : "Chat with Curio to build your style profile"}
            </p>
          </div>
        </div>

        {/* Profile cards */}
        <div className="space-y-4">
          {/* Style */}
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Tag className="h-4 w-4 text-violet-400" />
              <span className="text-sm font-semibold text-zinc-200">Your Style</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {prefs.style.length > 0 ? (
                prefs.style.map((s) => (
                  <span key={s} className="capitalize px-3 py-1 rounded-full bg-violet-900/30 border border-violet-500/30 text-violet-300 text-xs font-medium">
                    {s}
                  </span>
                ))
              ) : (
                <EmptyBadge label="Not set yet — ask Curio for style recommendations" />
              )}
            </div>
          </div>

          {/* Colors */}
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Palette className="h-4 w-4 text-violet-400" />
              <span className="text-sm font-semibold text-zinc-200">Preferred Colors</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {prefs.colors.length > 0 ? (
                prefs.colors.map((c) => (
                  <span key={c} className="capitalize px-3 py-1 rounded-full bg-zinc-800 border border-zinc-700/60 text-zinc-300 text-xs font-medium">
                    {c}
                  </span>
                ))
              ) : (
                <EmptyBadge label="Mention color preferences in Curio chat" />
              )}
            </div>
          </div>

          {/* Size + Budget */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <Ruler className="h-4 w-4 text-violet-400" />
                <span className="text-sm font-semibold text-zinc-200">Size</span>
              </div>
              {prefs.sizes.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {prefs.sizes.map((s) => (
                    <span key={s} className="uppercase text-xl font-black text-zinc-100">{s}</span>
                  ))}
                </div>
              ) : (
                <span className="text-zinc-600 text-sm italic">Not set</span>
              )}
            </div>
            <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <IndianRupee className="h-4 w-4 text-violet-400" />
                <span className="text-sm font-semibold text-zinc-200">Budget</span>
              </div>
              {prefs.budget_max ? (
                <>
                  <span className="text-2xl font-black text-zinc-100">₹{prefs.budget_max.toLocaleString()}</span>
                  <p className="text-[10px] text-zinc-500 mt-1">max per item</p>
                </>
              ) : (
                <span className="text-zinc-600 text-sm italic">Not set</span>
              )}
            </div>
          </div>

          {/* Occasions */}
          <div className="bg-zinc-900/80 border border-zinc-800/60 rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Calendar className="h-4 w-4 text-violet-400" />
              <span className="text-sm font-semibold text-zinc-200">Occasions</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {prefs.occasions.length > 0 ? (
                prefs.occasions.map((o) => (
                  <span key={o} className="capitalize px-3 py-1 rounded-full bg-zinc-800 border border-zinc-700/60 text-zinc-300 text-xs font-medium">
                    {o}
                  </span>
                ))
              ) : (
                <EmptyBadge label="Mention occasion in Curio e.g. 'for office'" />
              )}
            </div>
          </div>

          {/* Logged in as */}
          <div className="bg-zinc-900/50 border border-zinc-800/40 rounded-2xl p-4 flex items-center gap-3">
            <User className="h-4 w-4 text-zinc-500 flex-shrink-0" />
            <div>
              <p className="text-xs text-zinc-500">Logged in as</p>
              <p className="text-sm font-medium text-zinc-300">{user?.name} <span className="text-zinc-600">(@{user?.username})</span></p>
            </div>
          </div>

          {/* CTA */}
          <div className="bg-gradient-to-br from-violet-950/60 to-purple-950/40 border border-violet-700/30 rounded-2xl p-6 text-center">
            <MessageCircle className="h-8 w-8 text-violet-400 mx-auto mb-3" />
            <p className="text-sm font-semibold text-zinc-200 mb-1">
              {hasAnyPrefs ? "Keep refining your profile" : "Start building your profile"}
            </p>
            <p className="text-xs text-zinc-500 mb-4">
              {hasAnyPrefs
                ? "Every conversation with Curio makes your recommendations more personal"
                : "Chat with Curio — your style preferences will appear here automatically"}
            </p>
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
