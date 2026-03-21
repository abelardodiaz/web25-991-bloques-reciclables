"use client";

import {
  type ReactNode,
  type ReactElement,
  Children,
  isValidElement,
} from "react";
import { WizardContext } from "./wizard-context.js";
import { useFormWizard } from "../hooks/use-form-wizard.js";

export interface FormWizardProps {
  children: ReactNode;
  onComplete: (data: Record<string, unknown>) => void;
  completeBtnLabel?: string;
}

export function FormWizard({
  children,
  onComplete,
  completeBtnLabel: _completeBtnLabel = "Enviar",
}: FormWizardProps) {
  const childArray = Children.toArray(children).filter(
    (child): child is ReactElement => isValidElement(child),
  );

  const totalSteps = childArray.length;
  const wizard = useFormWizard(totalSteps);

  const handleComplete = () => {
    onComplete(wizard.data);
  };

  const contextValue = {
    ...wizard,
    handleComplete,
  };

  return (
    <WizardContext.Provider value={contextValue}>
      <div className="flex flex-col gap-4">
        {childArray.map((child, index) => (
          <div
            key={index}
            style={{
              display: index === wizard.currentStep ? "block" : "none",
            }}
          >
            {child}
          </div>
        ))}
      </div>
    </WizardContext.Provider>
  );
}
