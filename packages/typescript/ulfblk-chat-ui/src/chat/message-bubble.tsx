"use client";

import type { Message } from "../types.js";

export interface MessageBubbleProps {
  message: Message;
}

function formatTime(date: Date): string {
  const h = String(date.getHours()).padStart(2, "0");
  const m = String(date.getMinutes()).padStart(2, "0");
  return `${h}:${m}`;
}

const statusLabels: Record<string, string> = {
  sending: "...",
  sent: "v",
  delivered: "vv",
  read: "vv",
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isSent = message.direction === "sent";

  return (
    <div
      className={`flex ${isSent ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[75%] rounded-lg px-3 py-2 text-sm ${
          isSent
            ? "bg-[hsl(var(--bloque-primary))] text-[hsl(var(--bloque-primary-foreground))]"
            : "bg-[hsl(var(--bloque-muted))] text-[hsl(var(--bloque-foreground))]"
        }`}
      >
        <p>{message.text}</p>
        <div
          className={`mt-1 flex items-center gap-1 text-xs opacity-70 ${
            isSent ? "justify-end" : "justify-start"
          }`}
        >
          <span>{formatTime(message.timestamp)}</span>
          {isSent && message.status && (
            <span
              className={
                message.status === "read"
                  ? "text-blue-300"
                  : ""
              }
            >
              {statusLabels[message.status]}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
