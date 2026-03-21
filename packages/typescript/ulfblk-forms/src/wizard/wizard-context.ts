"use client";

import { createContext, useContext } from "react";

export interface WizardContextValue {
  currentStep: number;
  totalSteps: number;
  goNext: () => void;
  goPrev: () => void;
  isFirst: boolean;
  isLast: boolean;
  data: Record<string, unknown>;
  setField: (key: string, value: unknown) => void;
}

export const WizardContext = createContext<WizardContextValue | null>(null);

export function useWizardContext(): WizardContextValue {
  const ctx = useContext(WizardContext);
  if (!ctx) {
    throw new Error(
      "useWizardContext must be used inside <FormWizard>",
    );
  }
  return ctx;
}
