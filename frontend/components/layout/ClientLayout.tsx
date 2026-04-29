"use client";

import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/login") {
    return <>{children}</>;
  }

  return (
    <div className="flex h-full">
      <Sidebar />
      <main className="flex-1 ml-14 lg:ml-44 h-full overflow-hidden">
        {children}
      </main>
    </div>
  );
}
