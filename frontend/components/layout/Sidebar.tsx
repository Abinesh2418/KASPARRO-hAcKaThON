"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Home, MessageCircle, User, Sparkles, LogIn, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

const NAV_ITEMS = [
  { href: "/", label: "Home", icon: Home },
  { href: "/curio", label: "Curio AI", icon: MessageCircle },
  { href: "/profile", label: "Profile", icon: User },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<{ username: string; name: string } | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("curio_user");
      if (raw) setUser(JSON.parse(raw));
    } catch {}
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("curio_user");
    setUser(null);
    router.push("/login");
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-14 lg:w-44 flex flex-col bg-zinc-900/95 border-r border-zinc-800/60 z-40 backdrop-blur-sm">
      {/* Logo */}
      <div className="flex items-center gap-3 px-3 lg:px-4 py-5 border-b border-zinc-800/60">
        <div className="h-9 w-9 flex-shrink-0 rounded-xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-900/40">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <div className="hidden lg:block">
          <p className="text-sm font-bold text-zinc-100 leading-none">Shopify</p>
          <p className="text-[10px] text-zinc-500 mt-0.5">AI Fashion</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 p-2 flex-1 mt-2">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group",
                active
                  ? "bg-violet-600/20 text-violet-300 border border-violet-500/30 shadow-sm shadow-violet-900/20"
                  : "text-zinc-500 hover:text-zinc-100 hover:bg-zinc-800/80"
              )}
            >
              <Icon
                className={cn(
                  "h-5 w-5 flex-shrink-0 transition-transform duration-200",
                  active ? "text-violet-400" : "group-hover:scale-110"
                )}
              />
              <span className="hidden lg:block text-sm font-medium">{label}</span>
              {active && (
                <span className="hidden lg:block ml-auto h-1.5 w-1.5 rounded-full bg-violet-400" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="p-3 border-t border-zinc-800/60 flex flex-col gap-2">
        <div className="hidden lg:flex items-center gap-2 px-2 py-2 rounded-lg bg-violet-950/30 border border-violet-800/20">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse flex-shrink-0" />
          <p className="text-[10px] text-zinc-500">Online</p>
        </div>
        <div className="lg:hidden flex justify-center">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
        </div>
        {user ? (
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-2 py-2 rounded-lg text-zinc-500 hover:text-red-400 hover:bg-red-950/20 transition-colors w-full"
          >
            <LogOut className="h-4 w-4 flex-shrink-0" />
            <span className="hidden lg:block text-xs truncate">{user.name}</span>
          </button>
        ) : (
          <Link
            href="/login"
            className="flex items-center gap-2 px-2 py-2 rounded-lg text-zinc-500 hover:text-violet-400 hover:bg-violet-950/20 transition-colors"
          >
            <LogIn className="h-4 w-4 flex-shrink-0" />
            <span className="hidden lg:block text-xs">Sign In</span>
          </Link>
        )}
      </div>
    </aside>
  );
}
