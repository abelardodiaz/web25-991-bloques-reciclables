"use client";

import { useState, useCallback } from "react";
import type { Message } from "../types.js";

export interface UseChatReturn {
  messages: Message[];
  addMessage: (message: Message) => void;
  clearMessages: () => void;
}

export function useChat(initialMessages?: Message[]): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>(initialMessages ?? []);

  const addMessage = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, addMessage, clearMessages };
}
