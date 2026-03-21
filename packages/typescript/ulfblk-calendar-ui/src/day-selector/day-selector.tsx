"use client";

export interface DaySelectorProps {
  currentDate: Date;
  onChange: (date: Date) => void;
  prevLabel?: string;
  nextLabel?: string;
  todayLabel?: string;
  timezone?: string;
}

function formatDisplayDate(date: Date, timezone: string): string {
  try {
    return date.toLocaleDateString("es", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      timeZone: timezone,
    });
  } catch {
    return date.toLocaleDateString("es", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  }
}

export function DaySelector({
  currentDate,
  onChange,
  prevLabel = "Anterior",
  nextLabel = "Siguiente",
  todayLabel = "Hoy",
  timezone = "UTC",
}: DaySelectorProps) {
  const goToPrev = () => {
    const prev = new Date(currentDate);
    prev.setDate(prev.getDate() - 1);
    onChange(prev);
  };

  const goToNext = () => {
    const next = new Date(currentDate);
    next.setDate(next.getDate() + 1);
    onChange(next);
  };

  const goToToday = () => {
    onChange(new Date());
  };

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={goToPrev}
        className="rounded-md border border-[hsl(var(--bloque-border))] px-3 py-1.5 text-sm text-[hsl(var(--bloque-foreground))] hover:bg-[hsl(var(--bloque-accent))]"
      >
        {prevLabel}
      </button>
      <button
        type="button"
        onClick={goToToday}
        className="rounded-md border border-[hsl(var(--bloque-border))] px-3 py-1.5 text-sm text-[hsl(var(--bloque-foreground))] hover:bg-[hsl(var(--bloque-accent))]"
      >
        {todayLabel}
      </button>
      <button
        type="button"
        onClick={goToNext}
        className="rounded-md border border-[hsl(var(--bloque-border))] px-3 py-1.5 text-sm text-[hsl(var(--bloque-foreground))] hover:bg-[hsl(var(--bloque-accent))]"
      >
        {nextLabel}
      </button>
      <span className="text-sm font-medium text-[hsl(var(--bloque-foreground))]">
        {formatDisplayDate(currentDate, timezone)}
      </span>
    </div>
  );
}
