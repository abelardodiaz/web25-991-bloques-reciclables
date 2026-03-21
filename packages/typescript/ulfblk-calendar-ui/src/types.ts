export interface Slot {
  start: string; // "09:00"
  end: string; // "09:30"
  available: boolean;
}

export type SlotStatus = "available" | "selected" | "disabled";
