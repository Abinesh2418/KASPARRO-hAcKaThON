"use client";

import { useState } from "react";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { X, SquarePen, MessageCircle, Sparkles, Clock, Trash2 } from "lucide-react";
import type { SavedChat } from "@/types";


function formatChatDate(savedAt: number): string {
  const now = Date.now();
  const diff = now - savedAt;
  const oneDay = 86400_000;
  if (diff < oneDay) return "Today";
  if (diff < 2 * oneDay) return "Yesterday";
  if (diff < 7 * oneDay) return "This week";
  return "Earlier";
}

function groupHistory(history: SavedChat[]) {
  const groups: Record<string, SavedChat[]> = {};
  for (const chat of history) {
    const label = formatChatDate(chat.savedAt);
    if (!groups[label]) groups[label] = [];
    groups[label].push(chat);
  }
  return groups;
}

export function ChatInterface() {
  const { state, sendMessage, newChat, loadChat, deleteChat, clearHistory, chatHistory, bottomRef } = useChat();
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);

  const handleNewChat = () => {
    newChat();
    setActiveHistoryId(null);
  };

  const handleLoadChat = (chat: SavedChat) => {
    loadChat(chat);
    setActiveHistoryId(chat.id);
    setShowMobileMenu(false);
  };

  const historyGroups = groupHistory(chatHistory);
  const groupOrder = ["Today", "Yesterday", "This week", "Earlier"];
  const isEmpty = state.messages.length === 0;

  return (
    <div className="flex h-full w-full bg-zinc-950 overflow-hidden">

      {/* ── Left Sidebar ── */}
      <aside className="hidden lg:flex flex-col w-60 xl:w-64 flex-shrink-0 border-r border-zinc-800/60 bg-zinc-900/40">

        {/* New Chat */}
        <div className="p-3 border-b border-zinc-800/60">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl border border-zinc-700/60 text-sm text-zinc-300 hover:bg-zinc-800 hover:border-violet-500/40 hover:text-violet-300 transition-all group"
          >
            <SquarePen className="h-4 w-4 text-zinc-400 group-hover:text-violet-400 transition-colors flex-shrink-0" />
            <span className="font-medium">New Chat</span>
          </button>
        </div>

        {/* Current chat (if has messages and not a loaded history item) */}
        <div className="flex-1 overflow-y-auto p-2 space-y-4">
          {!isEmpty && (
            <div>
              <p className="text-[10px] font-semibold text-zinc-600 uppercase tracking-wider px-2 py-1.5">Current</p>
              <div className="flex items-start gap-2 px-3 py-2 rounded-xl bg-violet-600/10 border border-violet-500/20">
                <MessageCircle className="h-3.5 w-3.5 text-violet-400 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-zinc-300 leading-snug line-clamp-2">
                  {state.messages.find((m) => m.role === "user")?.content ?? "New conversation"}
                </p>
              </div>
            </div>
          )}

          {/* Chat history */}
          {chatHistory.length > 0 && (
            <div className="space-y-3">
              {groupOrder.map((label) => {
                const chats = historyGroups[label];
                if (!chats?.length) return null;
                return (
                  <div key={label}>
                    <p className="text-[10px] font-semibold text-zinc-600 uppercase tracking-wider px-2 py-1.5 flex items-center gap-1">
                      <Clock className="h-2.5 w-2.5" />
                      {label}
                    </p>
                    <div className="space-y-0.5">
                      {chats.map((chat) => (
                        <div
                          key={chat.id}
                          className={`flex items-center gap-1 rounded-xl transition-all group ${
                            activeHistoryId === chat.id
                              ? "bg-zinc-800 border border-zinc-700/60"
                              : "hover:bg-zinc-800/60"
                          }`}
                        >
                          <button
                            onClick={() => handleLoadChat(chat)}
                            className={`flex-1 min-w-0 text-left flex items-start gap-2 px-3 py-2 ${
                              activeHistoryId === chat.id ? "text-zinc-200" : "text-zinc-500 group-hover:text-zinc-300"
                            }`}
                          >
                            <MessageCircle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5 opacity-60" />
                            <span className="text-xs leading-snug line-clamp-2">{chat.title}</span>
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); deleteChat(chat.id); }}
                            className="flex-shrink-0 p-1.5 mr-1 rounded-lg text-zinc-700 hover:text-red-400 hover:bg-red-950/30 opacity-0 group-hover:opacity-100 transition-all"
                            title="Delete chat"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Empty history placeholder */}
          {isEmpty && chatHistory.length === 0 && (
            <div className="px-3 py-4 text-center">
              <Sparkles className="h-5 w-5 text-zinc-700 mx-auto mb-2" />
              <p className="text-xs text-zinc-600 leading-relaxed">Your conversations will appear here</p>
            </div>
          )}
        </div>

        {/* Clear all chats */}
        {chatHistory.length > 0 && (
          <div className="p-3 border-t border-zinc-800/60">
            <button
              onClick={clearHistory}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-xl text-xs text-zinc-600 hover:text-red-400 hover:bg-red-950/20 transition-all"
            >
              <Trash2 className="h-3.5 w-3.5 flex-shrink-0" />
              Delete all chats
            </button>
          </div>
        )}
      </aside>

      {/* ── Main chat area ── */}
      <div className="flex flex-1 flex-col min-w-0">

        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-zinc-800/60 flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center shadow-lg shadow-violet-900/30">
              <span className="text-sm font-black text-white">C</span>
            </div>
            <div>
              <h1 className="text-sm font-bold text-zinc-100 leading-none">Curio AI</h1>
              <p className="text-[10px] text-zinc-500 mt-0.5">AI Fashion Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 bg-emerald-900/30 border border-emerald-700/40 rounded-full px-2.5 py-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] text-emerald-400 font-medium">Live</span>
            </div>
            {/* Mobile: new chat */}
            <button
              onClick={handleNewChat}
              className="lg:hidden p-2 rounded-xl text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
            >
              <SquarePen className="h-4 w-4" />
            </button>
            {/* Mobile: history */}
            <button
              onClick={() => setShowMobileMenu(true)}
              className="lg:hidden p-2 rounded-xl text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors"
            >
              <MessageCircle className="h-4 w-4" />
            </button>
          </div>
        </header>

        {/* Error banner */}
        {state.error && (
          <div className="mx-4 mt-4 flex-shrink-0 rounded-xl border border-red-800/50 bg-red-950/30 px-4 py-3 text-xs text-red-400">
            {state.error}
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          {isEmpty ? (
            <div className="flex flex-col items-center justify-center h-full px-4 pb-4">
              <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center shadow-xl shadow-violet-900/40 mb-4">
                <Sparkles className="h-7 w-7 text-white" />
              </div>
              <h2 className="text-lg font-bold text-zinc-100 mb-1">What are you looking for?</h2>
              <p className="text-sm text-zinc-500 text-center max-w-xs">
                Describe your occasion, budget, or vibe — Curio finds the perfect fit.
              </p>
            </div>
          ) : (
            <MessageList messages={state.messages} bottomRef={bottomRef} />
          )}
        </div>


        {/* Input */}
        <div className="flex-shrink-0">
          <ChatInput
            onSend={sendMessage}
            isStreaming={state.isStreaming}
          />
        </div>
      </div>

      {/* ── Mobile history drawer ── */}
      {showMobileMenu && (
        <div className="lg:hidden fixed inset-0 z-50 flex flex-col justify-end">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowMobileMenu(false)}
          />
          <div className="relative z-10 rounded-t-3xl border-t border-zinc-700 bg-zinc-900 p-5 max-h-[70vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <p className="font-semibold text-zinc-100">Chat History</p>
              <button
                onClick={() => setShowMobileMenu(false)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <button
              onClick={() => { handleNewChat(); setShowMobileMenu(false); }}
              className="w-full flex items-center gap-2 px-4 py-3 rounded-xl bg-violet-600/20 border border-violet-500/30 text-violet-300 text-sm font-medium hover:bg-violet-600/30 transition-colors mb-3"
            >
              <SquarePen className="h-4 w-4" />
              New Chat
            </button>
            {chatHistory.length === 0 ? (
              <p className="text-xs text-zinc-600 text-center py-4">No previous chats</p>
            ) : (
              <div className="space-y-1">
                {chatHistory.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => handleLoadChat(chat)}
                    className="w-full text-left flex items-start gap-2 px-3 py-2.5 rounded-xl text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
                  >
                    <MessageCircle className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" />
                    <span className="text-xs leading-snug line-clamp-2">{chat.title}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
