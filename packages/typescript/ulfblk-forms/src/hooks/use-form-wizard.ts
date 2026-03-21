"use client";

import { useState, useCallback } from "react";

export interface UseFormWizardReturn {
  currentStep: number;
  totalSteps: number;
  goNext: () => void;
  goPrev: () => void;
  goTo: (step: number) => void;
  isFirst: boolean;
  isLast: boolean;
  data: Record<string, unknown>;
  setField: (key: string, value: unknown) => void;
}

export function useFormWizard(totalSteps: number): UseFormWizardReturn {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<Record<string, unknown>>({});

  const goNext = useCallback(() => {
    setCurrentStep((prev) => Math.min(prev + 1, totalSteps - 1));
  }, [totalSteps]);

  const goPrev = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const goTo = useCallback(
    (step: number) => {
      if (step >= 0 && step < totalSteps) {
        setCurrentStep(step);
      }
    },
    [totalSteps],
  );

  const setField = useCallback((key: string, value: unknown) => {
    setData((prev) => ({ ...prev, [key]: value }));
  }, []);

  return {
    currentStep,
    totalSteps,
    goNext,
    goPrev,
    goTo,
    isFirst: currentStep === 0,
    isLast: currentStep === totalSteps - 1,
    data,
    setField,
  };
}
