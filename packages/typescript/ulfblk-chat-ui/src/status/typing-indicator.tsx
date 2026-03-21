"use client";

export interface TypingIndicatorProps {
  label?: string;
}

export function TypingIndicator({
  label = "Escribiendo...",
}: TypingIndicatorProps) {
  return (
    <div className="flex items-center gap-2 px-3 py-1">
      <div className="flex gap-1">
        <span
          className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--bloque-muted-foreground))]"
          style={{ animationDelay: "0ms" }}
        />
        <span
          className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--bloque-muted-foreground))]"
          style={{ animationDelay: "150ms" }}
        />
        <span
          className="inline-block h-1.5 w-1.5 animate-bounce rounded-full bg-[hsl(var(--bloque-muted-foreground))]"
          style={{ animationDelay: "300ms" }}
        />
      </div>
      <span className="text-xs text-[hsl(var(--bloque-muted-foreground))]">
        {label}
      </span>
    </div>
  );
}
