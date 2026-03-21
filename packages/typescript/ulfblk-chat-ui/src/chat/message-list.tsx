"use client";

import type { Message } from "../types.js";
import { MessageBubble } from "./message-bubble.js";

export interface MessageListProps {
  messages: Message[];
  emptyLabel?: string;
}

export function MessageList({
  messages,
  emptyLabel = "No hay mensajes",
}: MessageListProps) {
  if (messages.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-[hsl(var(--bloque-muted-foreground))]">
        {emptyLabel}
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
    </div>
  );
}
