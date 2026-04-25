"use client";

import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";
import type { Message } from "@/types";
import { InlineProducts } from "@/components/products/InlineProducts";
import { TypingIndicator } from "./TypingIndicator";

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[75%] space-y-1.5">
          {message.imageUrl && (
            <div className="flex justify-end">
              <img
                src={message.imageUrl}
                alt="Uploaded"
                className="max-h-40 rounded-xl object-cover border border-violet-500/30 shadow-md"
              />
            </div>
          )}
          {message.content && (
            <div className="rounded-2xl rounded-tr-sm bg-violet-600 px-4 py-3 text-sm text-white shadow-lg shadow-violet-900/20">
              {message.content}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 mb-4">
      <div className="flex items-start gap-3">
        {/* Avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center text-xs font-bold text-white shadow-md">
          S
        </div>

        <div className="flex-1 min-w-0">
          {/* Message content */}
          <div
            className={cn(
              "rounded-2xl rounded-tl-sm px-4 py-3 text-sm shadow-sm",
              message.isError
                ? "bg-red-950/50 border border-red-800 text-red-300"
                : "bg-zinc-800/80 border border-zinc-700/50 text-zinc-100"
            )}
          >
            {message.isStreaming && !message.content ? (
              <TypingIndicator />
            ) : (
              <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-p:my-1">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
            {/* Streaming cursor */}
            {message.isStreaming && message.content && (
              <span className="inline-block w-0.5 h-4 bg-violet-400 animate-pulse ml-0.5 align-middle" />
            )}
          </div>
        </div>
      </div>

      {/* Inline product recommendations */}
      {message.products && message.products.length > 0 && (
        <div className="ml-11">
          <InlineProducts products={message.products} />
        </div>
      )}
    </div>
  );
}
