"use client";

import { useState, type KeyboardEvent } from "react";

export interface ChatInputProps {
  onSend: (text: string) => void;
  placeholder?: string;
  sendLabel?: string;
}

export function ChatInput({
  onSend,
  placeholder = "Escribe un mensaje...",
  sendLabel = "Enviar",
}: ChatInputProps) {
  const [text, setText] = useState("");

  const handleSend = () => {
    const trimmed = text.trim();
    if (trimmed.length === 0) return;
    onSend(trimmed);
    setText("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-center gap-2 border-t border-[hsl(var(--bloque-border))] p-3">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className="flex-1 rounded-md border border-[hsl(var(--bloque-border))] bg-[hsl(var(--bloque-background))] px-3 py-2 text-sm text-[hsl(var(--bloque-foreground))] placeholder:text-[hsl(var(--bloque-muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--bloque-ring))]"
      />
      <button
        type="button"
        onClick={handleSend}
        disabled={text.trim().length === 0}
        className="rounded-md bg-[hsl(var(--bloque-primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--bloque-primary-foreground))] hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {sendLabel}
      </button>
    </div>
  );
}
