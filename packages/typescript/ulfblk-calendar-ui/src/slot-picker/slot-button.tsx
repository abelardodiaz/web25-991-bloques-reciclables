"use client";

import type { Slot } from "../types.js";

export interface SlotButtonProps {
  slot: Slot;
  selected: boolean;
  onClick: () => void;
  disabledLabel?: string;
}

export function SlotButton({
  slot,
  selected,
  onClick,
  disabledLabel = "No disponible",
}: SlotButtonProps) {
  const baseClasses =
    "rounded-md px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1";

  if (!slot.available) {
    return (
      <button
        type="button"
        disabled
        className={`${baseClasses} cursor-not-allowed bg-[hsl(var(--bloque-muted))] text-[hsl(var(--bloque-muted-foreground))] opacity-50`}
        aria-label={`${slot.start} - ${slot.end}: ${disabledLabel}`}
      >
        {slot.start}
      </button>
    );
  }

  if (selected) {
    return (
      <button
        type="button"
        onClick={onClick}
        className={`${baseClasses} bg-[hsl(var(--bloque-primary))] text-[hsl(var(--bloque-primary-foreground))] ring-[hsl(var(--bloque-ring))]`}
        aria-pressed="true"
        aria-label={`${slot.start} - ${slot.end}: seleccionado`}
      >
        {slot.start}
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${baseClasses} border border-[hsl(var(--bloque-border))] bg-[hsl(var(--bloque-card))] text-[hsl(var(--bloque-foreground))] hover:bg-[hsl(var(--bloque-accent))]`}
      aria-pressed="false"
      aria-label={`${slot.start} - ${slot.end}: disponible`}
    >
      {slot.start}
    </button>
  );
}
