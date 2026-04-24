"use client";

import { useReducer, useRef, useCallback } from "react";
import type { ChatState, ChatAction, Message, Preferences } from "@/types";
import { streamChat } from "@/services/api";
import { generateId } from "@/lib/utils";

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

function reducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "ADD_USER_MESSAGE":
      return {
        ...state,
        isStreaming: true,
        error: null,
        messages: [
          ...state.messages,
          { id: action.payload.id, role: "user", content: action.payload.content },
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
            ? { ...m, products: action.payload.products, isStreaming: false }
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

    default:
      return state;
  }
}

export function useChat() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  const getHistoryMessages = (messages: Message[]) =>
    messages
      .filter((m) => !m.isError)
      .map((m) => ({ role: m.role, content: m.content }));

  const sendMessage = useCallback(
    async (prompt: string) => {
      if (!prompt.trim() || state.isStreaming) return;

      const userMsgId = generateId();
      const assistantMsgId = generateId();

      dispatch({ type: "ADD_USER_MESSAGE", payload: { id: userMsgId, content: prompt } });
      dispatch({ type: "START_ASSISTANT_MESSAGE", payload: { id: assistantMsgId } });
      setTimeout(scrollToBottom, 50);

      try {
        const history = getHistoryMessages(state.messages);

        for await (const event of streamChat(prompt, state.sessionId, history)) {
          switch (event.type) {
            case "session_id":
              dispatch({ type: "SET_SESSION_ID", payload: event.session_id! });
              break;
            case "token":
              dispatch({ type: "APPEND_TOKEN", payload: { id: assistantMsgId, token: event.content! } });
              scrollToBottom();
              break;
            case "metadata":
              dispatch({
                type: "SET_METADATA",
                payload: {
                  id: assistantMsgId,
                  products: event.products ?? [],
                  preferences: event.preferences ?? initialPreferences,
                },
              });
              break;
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

  return { state, sendMessage, bottomRef, scrollToBottom };
}
