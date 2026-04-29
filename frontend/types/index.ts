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
  variant_id?: string;
  variants?: Array<{ id: string; size: string | null; price: number }>;
  merchant_name?: string;
  merchant_url?: string;
}

export interface Preferences {
  style: string[];
  colors: string[];
  sizes: string[];
  budget_max: number | null;
  budget_min: number | null;
  occasions: string[];
}

export interface CheckoutLineItem {
  title: string;
  size: string;
  color?: string;
  price: number;
  quantity: number;
  image: string;
  subtotal_for_line: number;
}

export interface MerchantCheckout {
  step: number;
  merchant_name: string;
  merchant_url: string;
  cart_lines: Array<{ merchandiseId: string; quantity: number }>;
  items: CheckoutLineItem[];
  subtotal: number;
  item_count: number;
  checkout_url: string | null;
}

export interface CheckoutMetadata {
  show_checkout_cta: boolean;
  show_cart_summary: boolean;
  is_multi_merchant: boolean;
  merchant_count: number;
  checkouts: MerchantCheckout[];
  grand_total: number;
  total_items: number;
  currency: string;
}

export interface ScoredProductDimensions {
  occasion_fit: number;
  style_match: number;
  budget_fit: number;
  category_match: number;
  color_match: number;
  stock_availability: number;
  value_score: number;
}

export interface ScoredProduct {
  product_id: string;
  title: string;
  price: number;
  score: number;
  dimension_scores: ScoredProductDimensions;
}

export interface TradeoffPanel {
  id: string;
  title: string;
  product_id: string;
  highlight: string;
  tradeoff: string;
  quick_replies: string[];
}

export interface TradeoffData {
  scored_products: ScoredProduct[];
  tradeoff_panels: TradeoffPanel[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  products?: Product[];
  isStreaming?: boolean;
  isError?: boolean;
  imageUrl?: string;
  metadata?: CheckoutMetadata;
  tradeoffData?: TradeoffData;
}

export interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  sessionId: string | null;
  preferences: Preferences;
  error: string | null;
}

export type ChatAction =
  | { type: "ADD_USER_MESSAGE"; payload: { id: string; content: string; imageUrl?: string } }
  | { type: "START_ASSISTANT_MESSAGE"; payload: { id: string } }
  | { type: "APPEND_TOKEN"; payload: { id: string; token: string } }
  | { type: "SET_SESSION_ID"; payload: string }
  | { type: "SET_METADATA"; payload: { id: string; products: Product[]; preferences: Preferences; checkoutMetadata?: CheckoutMetadata; tradeoffData?: TradeoffData } }
  | { type: "FINISH_STREAMING" }
  | { type: "SET_ERROR"; payload: string }
  | { type: "CLEAR_ERROR" }
  | { type: "CLEAR_CHAT" }
  | { type: "LOAD_CHAT"; payload: { messages: Message[]; sessionId: string | null; preferences: Preferences } };

export interface SavedChat {
  id: string;
  title: string;
  messages: Message[];
  sessionId: string | null;
  preferences: Preferences;
  savedAt: number;
}

export interface VisualSearchResult {
  attributes: {
    keywords?: string[];
    style: string[];
    colors: string[];
    silhouette?: string;
    category: string;
    material_guess?: string;
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
  auto_cart_product?: Product;
  auto_cart_products?: Product[];
  // Checkout fields
  show_checkout_cta?: boolean;
  show_cart_summary?: boolean;
  is_multi_merchant?: boolean;
  merchant_count?: number;
  checkouts?: MerchantCheckout[];
  grand_total?: number;
  total_items?: number;
  currency?: string;
  // Tradeoff matrix fields
  scored_products?: ScoredProduct[];
  tradeoff_panels?: TradeoffPanel[];
}

export interface CartItem {
  product_id: string;
  title: string;
  price: number;
  image: string;
  size: string | null;
  quantity: number;
  username: string;
  variant_id?: string;
  merchant_url?: string;
  merchant_name?: string;
}

export interface AuthUser {
  username: string;
  name: string;
}
