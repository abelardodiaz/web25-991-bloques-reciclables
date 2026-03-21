import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SlotPicker } from "../slot-picker/slot-picker.js";
import { SlotButton } from "../slot-picker/slot-button.js";
import type { Slot } from "../types.js";

const sampleSlots: Slot[] = [
  { start: "09:00", end: "09:30", available: true },
  { start: "09:30", end: "10:00", available: true },
  { start: "10:00", end: "10:30", available: false },
];

describe("SlotPicker", () => {
  it("renders all slots", () => {
    render(<SlotPicker slots={sampleSlots} onSelect={() => {}} />);
    expect(screen.getByText("09:00")).toBeDefined();
    expect(screen.getByText("09:30")).toBeDefined();
    expect(screen.getByText("10:00")).toBeDefined();
  });

  it("shows empty label when no slots", () => {
    render(<SlotPicker slots={[]} onSelect={() => {}} />);
    expect(screen.getByText("No hay horarios disponibles")).toBeDefined();
  });

  it("shows custom empty label", () => {
    render(
      <SlotPicker
        slots={[]}
        onSelect={() => {}}
        emptyLabel="Sin horarios"
      />,
    );
    expect(screen.getByText("Sin horarios")).toBeDefined();
  });

  it("calls onSelect when available slot is clicked", () => {
    const onSelect = vi.fn();
    render(<SlotPicker slots={sampleSlots} onSelect={onSelect} />);
    fireEvent.click(screen.getByText("09:00"));
    expect(onSelect).toHaveBeenCalledWith(sampleSlots[0]);
  });
});

describe("SlotButton", () => {
  it("renders disabled slot", () => {
    const slot: Slot = { start: "10:00", end: "10:30", available: false };
    render(<SlotButton slot={slot} selected={false} onClick={() => {}} />);
    const button = screen.getByRole("button");
    expect(button).toBeDefined();
    expect((button as HTMLButtonElement).disabled).toBe(true);
  });
});
