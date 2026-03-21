"use client";

import type { Slot } from "../types.js";
import { SlotButton } from "../slot-picker/slot-button.js";

export interface WeekViewProps {
  startDate: Date;
  slotsByDay: Record<string, Slot[]>;
  onSelectSlot: (date: string, slot: Slot) => void;
  dayLabels?: string[];
  selectedSlots?: Record<string, Slot>;
}

function formatDateKey(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export function WeekView({
  startDate,
  slotsByDay,
  onSelectSlot,
  dayLabels = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"],
  selectedSlots = {},
}: WeekViewProps) {
  const days: { label: string; dateKey: string }[] = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(startDate);
    d.setDate(d.getDate() + i);
    days.push({
      label: dayLabels[i % dayLabels.length],
      dateKey: formatDateKey(d),
    });
  }

  return (
    <div className="grid grid-cols-7 gap-2">
      {days.map((day) => {
        const daySlots = slotsByDay[day.dateKey] ?? [];
        const selected = selectedSlots[day.dateKey];
        return (
          <div key={day.dateKey} className="flex flex-col gap-1">
            <div className="pb-1 text-center text-xs font-semibold text-[hsl(var(--bloque-muted-foreground))]">
              <span>{day.label}</span>
              <br />
              <span className="text-[hsl(var(--bloque-foreground))]">
                {day.dateKey.slice(8)}
              </span>
            </div>
            <div className="flex flex-col gap-1">
              {daySlots.map((slot) => (
                <SlotButton
                  key={`${day.dateKey}-${slot.start}`}
                  slot={slot}
                  selected={
                    selected !== undefined &&
                    selected.start === slot.start &&
                    selected.end === slot.end
                  }
                  onClick={() => onSelectSlot(day.dateKey, slot)}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
