import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { WeekView } from "../week-view/week-view.js";
import type { Slot } from "../types.js";

describe("WeekView", () => {
  it("renders day labels", () => {
    const startDate = new Date(2026, 0, 5); // Monday Jan 5, 2026
    render(
      <WeekView
        startDate={startDate}
        slotsByDay={{}}
        onSelectSlot={() => {}}
      />,
    );
    expect(screen.getByText("Lun")).toBeDefined();
    expect(screen.getByText("Mar")).toBeDefined();
    expect(screen.getByText("Dom")).toBeDefined();
  });

  it("renders slots for a given day", () => {
    const startDate = new Date(2026, 0, 5);
    const slotsByDay: Record<string, Slot[]> = {
      "2026-01-05": [
        { start: "09:00", end: "09:30", available: true },
        { start: "10:00", end: "10:30", available: true },
      ],
    };
    render(
      <WeekView
        startDate={startDate}
        slotsByDay={slotsByDay}
        onSelectSlot={() => {}}
      />,
    );
    expect(screen.getByText("09:00")).toBeDefined();
    expect(screen.getByText("10:00")).toBeDefined();
  });

  it("calls onSelectSlot when a slot is clicked", () => {
    const onSelectSlot = vi.fn();
    const startDate = new Date(2026, 0, 5);
    const slot: Slot = { start: "09:00", end: "09:30", available: true };
    const slotsByDay: Record<string, Slot[]> = {
      "2026-01-05": [slot],
    };
    render(
      <WeekView
        startDate={startDate}
        slotsByDay={slotsByDay}
        onSelectSlot={onSelectSlot}
      />,
    );
    fireEvent.click(screen.getByText("09:00"));
    expect(onSelectSlot).toHaveBeenCalledWith("2026-01-05", slot);
  });
});
