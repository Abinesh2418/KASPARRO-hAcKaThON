export interface Product {
  id: string;
  title: string;
  price: number;
  compare_at_price?: number;
  images: string[];
  category: string;
  colors: string[];
  sizes: string[];
  style: string[];
  tags: string[];
  description: string;
  rating: number;
  reviews_count: number;
}

export interface Preferences {
  style: string[];
  colors: string[];
  sizes: string[];
  budget_max: number | null;
  budget_min: number | null;
  occasions: string[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  isStreaming?: boolean;
  isError?: boolean;
}

export interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  sessionId: string | null;
  preferences: Preferences;
  error: string | null;
}

export type ChatAction =
  | { type: "ADD_USER_MESSAGE"; payload: { id: string; content: string } }
  | { type: "START_ASSISTANT_MESSAGE"; payload: { id: string } }
  | { type: "APPEND_TOKEN"; payload: { id: string; token: string } }
  | { type: "SET_SESSION_ID"; payload: string }
  | { type: "SET_METADATA"; payload: { id: string; products: Product[]; preferences: Preferences } }
  | { type: "FINISH_STREAMING" }
  | { type: "SET_ERROR"; payload: string }
  | { type: "CLEAR_ERROR" };

export interface VisualSearchResult {
  attributes: {
    style: string[];
    colors: string[];
    silhouette: string;
    category: string;
    material_guess: string;
    occasion: string[];
    description: string;
  };
  products: Product[];
}

export interface SSEEvent {
  type: "session_id" | "token" | "metadata" | "done" | "error";
  session_id?: string;
  content?: string;
  preferences?: Preferences;
  products?: Product[];
  message?: string;
}
