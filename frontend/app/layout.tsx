import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { Sidebar } from "@/components/layout/Sidebar";
import "./globals.css";

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Shopify — AI Fashion Shopping",
  description: "Your personal AI shopping assistant. Find fashion that fits your vibe.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${geist.variable} h-full dark`}>
      <body className="h-full bg-zinc-950 antialiased">
        <div className="flex h-full">
          <Sidebar />
          <main className="flex-1 ml-16 lg:ml-56 h-full overflow-hidden">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
