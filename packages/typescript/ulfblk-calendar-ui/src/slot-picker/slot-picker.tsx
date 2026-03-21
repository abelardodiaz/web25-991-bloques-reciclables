"use client";

import type { Slot } from "../types.js";
import { SlotButton } from "./slot-button.js";

export interface SlotPickerProps {
  slots: Slot[];
  onSelect: (slot: Slot) => void;
  selectedSlot?: Slot;
  emptyLabel?: string;
}

export function SlotPicker({
  slots,
  onSelect,
  selectedSlot,
  emptyLabel = "No hay horarios disponibles",
}: SlotPickerProps) {
  if (slots.length === 0) {
    return (
      <p className="py-4 text-center text-sm text-[hsl(var(--bloque-muted-foreground))]">
        {emptyLabel}
      </p>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-6">
      {slots.map((slot) => (
        <SlotButton
          key={`${slot.start}-${slot.end}`}
          slot={slot}
          selected={
            selectedSlot !== undefined &&
            selectedSlot.start === slot.start &&
            selectedSlot.end === slot.end
          }
          onClick={() => onSelect(slot)}
        />
      ))}
    </div>
  );
}
