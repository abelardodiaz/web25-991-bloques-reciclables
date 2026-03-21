"use client";

import { useRef, useEffect, type ReactNode } from "react";

export interface ChatContainerProps {
  children: ReactNode;
}

export function ChatContainer({ children }: ChatContainerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  });

  return (
    <div
      ref={containerRef}
      className="flex flex-1 flex-col gap-2 overflow-y-auto p-4"
    >
      {children}
    </div>
  );
}
