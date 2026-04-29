"use client";

import { useReducer, useRef, useCallback, useEffect, useState } from "react";
import type { ChatState, ChatAction, Message, Preferences, SavedChat } from "@/types";
import { streamChat, addToCart, visualSearch } from "@/services/api";
import { generateId } from "@/lib/utils";

function getLoggedInUsername(): string {
  if (typeof window === "undefined") return "guest";
  try {
    const raw = localStorage.getItem("curio_user");
    return raw ? JSON.parse(raw).username : "guest";
  } catch {
    return "guest";
  }
}

const STORAGE_KEY = "curio-chat-state";
const HISTORY_KEY = "curio-chat-history";

const initialPreferences: Preferences = {
  style: [],
  colors: [],
  sizes: [],
  budget_max: null,
  budget_min: null,
  occasions: [],
};

const initialState: ChatState = {
  messages: [],
  isStreaming: false,
  sessionId: null,
  preferences: initialPreferences,
  error: null,
};

function loadFromStorage(): ChatState {
  if (typeof window === "undefined") return initialState;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return initialState;
    const saved = JSON.parse(raw);
    return {
      ...initialState,
      messages: (saved.messages ?? []).map((m: Message) => ({ ...m, isStreaming: false })),
      sessionId: saved.sessionId ?? null,
      preferences: saved.preferences ?? initialPreferences,
    };
  } catch {
    return initialState;
  }
}

function loadHistory(): SavedChat[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function reducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "ADD_USER_MESSAGE":
      return {
        ...state,
        isStreaming: true,
        error: null,
        messages: [
          ...state.messages,
          { id: action.payload.id, role: "user", content: action.payload.content, imageUrl: action.payload.imageUrl },
        ],
      };

    case "START_ASSISTANT_MESSAGE":
      return {
        ...state,
        messages: [
          ...state.messages,
          { id: action.payload.id, role: "assistant", content: "", isStreaming: true },
        ],
      };

    case "APPEND_TOKEN":
      return {
        ...state,
        messages: state.messages.map((m) =>
          m.id === action.payload.id
            ? { ...m, content: m.content + action.payload.token }
            : m
        ),
      };

    case "SET_SESSION_ID":
      return { ...state, sessionId: action.payload };

    case "SET_METADATA":
      return {
        ...state,
        preferences: action.payload.preferences,
        messages: state.messages.map((m) =>
          m.id === action.payload.id
            ? { ...m, products: action.payload.products, isStreaming: false, metadata: action.payload.checkoutMetadata, tradeoffData: action.payload.tradeoffData }
            : m
        ),
      };

    case "FINISH_STREAMING":
      return {
        ...state,
        isStreaming: false,
        messages: state.messages.map((m) =>
          m.isStreaming ? { ...m, isStreaming: false } : m
        ),
      };

    case "SET_ERROR":
      return {
        ...state,
        isStreaming: false,
        error: action.payload,
        messages: state.messages.map((m) =>
          m.isStreaming ? { ...m, isStreaming: false, isError: true } : m
        ),
      };

    case "CLEAR_ERROR":
      return { ...state, error: null };

    case "CLEAR_CHAT":
      return { ...initialState };

    case "LOAD_CHAT":
      return {
        ...initialState,
        messages: action.payload.messages.map((m) => ({ ...m, isStreaming: false })),
        sessionId: action.payload.sessionId,
        preferences: action.payload.preferences,
      };

    default:
      return state;
  }
}

export function useChat() {
  const [state, dispatch] = useReducer(reducer, undefined, loadFromStorage);
  const [chatHistory, setChatHistory] = useState<SavedChat[]>(loadHistory);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        messages: state.messages,
        sessionId: state.sessionId,
        preferences: state.preferences,
      })
    );
  }, [state.messages, state.sessionId, state.preferences]);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const getHistoryMessages = (messages: Message[]) =>
    messages
      .filter((m) => !m.isError)
      .map((m) => ({ role: m.role, content: m.content }));

  const saveCurrentToHistory = useCallback(
    (currentState: ChatState, existingHistory: SavedChat[], excludeId?: string): SavedChat[] => {
      if (currentState.messages.length === 0) return existingHistory;
      const firstUserMsg = currentState.messages.find((m) => m.role === "user");
      if (!firstUserMsg) return existingHistory;
      const chatId = currentState.sessionId ?? generateId();
      const title = firstUserMsg.content.slice(0, 60) + (firstUserMsg.content.length > 60 ? "…" : "");
      const saved: SavedChat = {
        id: chatId,
        title,
        messages: currentState.messages,
        sessionId: currentState.sessionId,
        preferences: currentState.preferences,
        savedAt: Date.now(),
      };
      return [saved, ...existingHistory.filter((c) => c.id !== chatId && c.id !== excludeId)].slice(0, 30);
    },
    []
  );

  const newChat = useCallback(() => {
    const updatedHistory = saveCurrentToHistory(state, chatHistory);
    setChatHistory(updatedHistory);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
    dispatch({ type: "CLEAR_CHAT" });
    localStorage.removeItem(STORAGE_KEY);
  }, [state, chatHistory, saveCurrentToHistory]);

  const loadChat = useCallback(
    (chat: SavedChat) => {
      const updatedHistory = saveCurrentToHistory(state, chatHistory, chat.id);
      setChatHistory(updatedHistory);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
      dispatch({
        type: "LOAD_CHAT",
        payload: { messages: chat.messages, sessionId: chat.sessionId, preferences: chat.preferences },
      });
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ messages: chat.messages, sessionId: chat.sessionId, preferences: chat.preferences })
      );
    },
    [state, chatHistory, saveCurrentToHistory]
  );

  const clearChat = useCallback(() => {
    dispatch({ type: "CLEAR_CHAT" });
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const deleteChat = useCallback((id: string) => {
    const updated = chatHistory.filter((c) => c.id !== id);
    setChatHistory(updated);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
  }, [chatHistory]);

  const clearHistory = useCallback(() => {
    setChatHistory([]);
    localStorage.removeItem(HISTORY_KEY);
  }, []);

  const sendMessage = useCallback(
    async (prompt: string, file?: File) => {
      if (!prompt.trim() || state.isStreaming) return;

      let enhancedPrompt = prompt;
      let imageUrl: string | undefined;
      let visualProducts: unknown[] | undefined;

      if (file) {
        imageUrl = URL.createObjectURL(file);
      }

      // Show user message + typing indicator IMMEDIATELY — don't wait for Ollama
      const userMsgId = generateId();
      const assistantMsgId = generateId();
      dispatch({ type: "ADD_USER_MESSAGE", payload: { id: userMsgId, content: prompt, imageUrl } });
      dispatch({ type: "START_ASSISTANT_MESSAGE", payload: { id: assistantMsgId } });
      setTimeout(scrollToBottom, 50);

      if (file) {
        try {
          const result = await visualSearch(file);
          const { attributes, products } = result;
          if (products && products.length > 0) {
            visualProducts = products;
          }
          const attrParts = [
            attributes.keywords?.length ? `Product: ${attributes.keywords.join(", ")}` : null,
            attributes.description,
            attributes.style?.length ? `Style: ${attributes.style.join(", ")}` : null,
            attributes.colors?.length ? `Colors: ${attributes.colors.join(", ")}` : null,
            attributes.category ? `Category: ${attributes.category}` : null,
            attributes.occasion?.length ? `Occasion: ${attributes.occasion.join(", ")}` : null,
          ].filter(Boolean).join(". ");
          enhancedPrompt = `[Image context: ${attrParts}]\n\n${prompt}`;
        } catch {
          // visual search failed, use original prompt
        }
      }

      try {
        const history = getHistoryMessages(state.messages);

        const username = getLoggedInUsername();
        for await (const event of streamChat(enhancedPrompt, state.sessionId, history, visualProducts, username)) {
          switch (event.type) {
            case "session_id":
              dispatch({ type: "SET_SESSION_ID", payload: event.session_id! });
              break;
            case "token":
              dispatch({ type: "APPEND_TOKEN", payload: { id: assistantMsgId, token: event.content! } });
              scrollToBottom();
              break;
            case "metadata": {
              const checkoutMetadata = event.show_cart_summary
                ? {
                    show_checkout_cta: event.show_checkout_cta ?? false,
                    show_cart_summary: event.show_cart_summary ?? false,
                    is_multi_merchant: event.is_multi_merchant ?? false,
                    merchant_count: event.merchant_count ?? 0,
                    checkouts: event.checkouts ?? [],
                    grand_total: event.grand_total ?? 0,
                    total_items: event.total_items ?? 0,
                    currency: event.currency ?? "INR",
                  }
                : undefined;
              const tradeoffData =
                event.scored_products && event.scored_products.length >= 1
                  ? { scored_products: event.scored_products, tradeoff_panels: event.tradeoff_panels ?? [] }
                  : undefined;
              dispatch({
                type: "SET_METADATA",
                payload: {
                  id: assistantMsgId,
                  products: event.products ?? [],
                  preferences: event.preferences ?? initialPreferences,
                  checkoutMetadata,
                  tradeoffData,
                },
              });
              const productsToAdd = event.auto_cart_products ?? (event.auto_cart_product ? [event.auto_cart_product] : []);

              if (productsToAdd.length > 0) {
                productsToAdd.forEach((p) => {
                  addToCart({
                    username,
                    product_id: p.id,
                    title: p.title,
                    price: p.price,
                    image: p.images?.[0] ?? "",
                    size: null,
                    variant_id: p.variant_id,
                    merchant_url: p.merchant_url,
                    merchant_name: p.merchant_name,
                  }).catch(console.error);
                });
              }
              break;
            }
            case "done":
              dispatch({ type: "FINISH_STREAMING" });
              break;
            case "error":
              dispatch({ type: "SET_ERROR", payload: event.message ?? "Unknown error" });
              break;
          }
        }
      } catch (err) {
        dispatch({
          type: "SET_ERROR",
          payload: err instanceof Error ? err.message : "Connection failed",
        });
      }
    },
    [state.isStreaming, state.sessionId, state.messages, scrollToBottom]
  );

  return { state, sendMessage, newChat, loadChat, clearChat, deleteChat, clearHistory, chatHistory, bottomRef, scrollToBottom };
}
