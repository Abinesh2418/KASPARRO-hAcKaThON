import type { SSEEvent, VisualSearchResult, CartItem, AuthUser } from "@/types";

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

export async function login(username: string, password: string): Promise<AuthUser> {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Invalid username or password");
  return res.json();
}

export async function fetchCart(username: string): Promise<CartItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/cart?username=${username}`, { cache: "no-store" });
  if (!res.ok) return [];
  const data = await res.json();
  return data.items ?? [];
}

export async function addToCart(item: Omit<CartItem, "quantity">): Promise<CartItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/cart`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  if (!res.ok) throw new Error("Failed to add to cart");
  const data = await res.json();
  return data.items ?? [];
}

export async function removeFromCart(productId: string, username: string): Promise<CartItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/cart/${productId}?username=${username}`, {
    method: "DELETE",
  });
  if (!res.ok) return [];
  const data = await res.json();
  return data.items ?? [];
}
