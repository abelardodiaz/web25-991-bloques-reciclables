# @ulfblk/calendar-ui

React calendar components - slot picker, week view, day selector. Zero external dependencies (only React + Tailwind CSS variables).

## Install

```bash
pnpm add @ulfblk/calendar-ui
```

## Quick Start

```tsx
import { SlotPicker, DaySelector, useCalendar } from "@ulfblk/calendar-ui";
import type { Slot } from "@ulfblk/calendar-ui";

const slots: Slot[] = [
  { start: "09:00", end: "09:30", available: true },
  { start: "09:30", end: "10:00", available: true },
  { start: "10:00", end: "10:30", available: false },
];

function BookingPage() {
  const { currentDate, goToNext, goToPrev, goToToday } = useCalendar();

  return (
    <div>
      <DaySelector
        currentDate={currentDate}
        onChange={(d) => console.log(d)}
      />
      <SlotPicker
        slots={slots}
        onSelect={(slot) => console.log("Selected:", slot)}
      />
    </div>
  );
}
```

## Components

| Component | Description |
|-----------|-------------|
| `SlotPicker` | Grid of time slot buttons with selection state |
| `SlotButton` | Individual slot button (available/selected/disabled) |
| `WeekView` | 7-column week layout with slots per day |
| `DaySelector` | Prev/Next/Today navigation with date display |

## Hooks

| Hook | Description |
|------|-------------|
| `useCalendar(initialDate?)` | Date navigation state: currentDate, goToNext, goToPrev, goToToday, setDate |

## i18n

All text labels are configurable via props with Spanish defaults:

- `emptyLabel` - "No hay horarios disponibles"
- `prevLabel` - "Anterior"
- `nextLabel` - "Siguiente"
- `todayLabel` - "Hoy"
- `dayLabels` - ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
