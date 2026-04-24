"use client";

import { useEffect } from "react";
import type { Message } from "@/types";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: Message[];
  bottomRef: React.RefObject<HTMLDivElement | null>;
}

export function MessageList({ messages, bottomRef }: Props) {
  const allMessages = messages;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, bottomRef]);

  return (
    <div className="flex flex-col px-4 py-6 space-y-1">
      {allMessages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
