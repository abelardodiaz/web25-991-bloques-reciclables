"use client";

import type { ReactNode } from "react";

export interface WizardStepProps {
  title: string;
  children: ReactNode;
}

export function WizardStep({ title, children }: WizardStepProps) {
  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-lg font-semibold text-[hsl(var(--bloque-foreground))]">
        {title}
      </h3>
      {children}
    </div>
  );
}
