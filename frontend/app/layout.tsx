import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import { ClientLayout } from "@/components/layout/ClientLayout";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  variable: "--font-jakarta",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Shopify — AI Fashion Shopping",
  description: "Your personal AI shopping assistant. Find fashion that fits your vibe.",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${jakarta.variable} h-full dark`}>
      <body className="h-full bg-zinc-950 antialiased">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
