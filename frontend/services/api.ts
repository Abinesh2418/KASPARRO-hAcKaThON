import type { SSEEvent, VisualSearchResult, Product } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function* streamChat(
  prompt: string,
  sessionId: string | null,
  messages: Array<{ role: string; content: string }>
): AsyncGenerator<SSEEvent> {
  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, session_id: sessionId, messages }),
    signal: AbortSignal.timeout(120_000),
  });

  if (!res.ok) {
    const err = await res.text().catch(() => "Unknown error");
    yield { type: "error", message: err };
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6)) as SSEEvent;
        } catch {
          // malformed chunk — skip
        }
      }
    }
  }
}

export async function visualSearch(file: File): Promise<VisualSearchResult> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/api/v1/visual-search`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new Error((await res.text()) || "Visual search failed");
  }
  return res.json();
}

export async function fetchPreferences(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/v1/preferences/${sessionId}`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchProducts(category?: string): Promise<Product[]> {
  const url = new URL(`${API_BASE}/api/v1/products`);
  if (category) url.searchParams.set("category", category);
  url.searchParams.set("limit", "20");
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.products ?? [];
}
