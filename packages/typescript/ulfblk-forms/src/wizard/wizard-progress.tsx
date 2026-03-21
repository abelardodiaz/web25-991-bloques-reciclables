"use client";

export interface WizardProgressProps {
  currentStep: number;
  totalSteps: number;
  stepLabels?: string[];
}

export function WizardProgress({
  currentStep,
  totalSteps,
  stepLabels,
}: WizardProgressProps) {
  const steps = Array.from({ length: totalSteps }, (_, i) => i);

  return (
    <div className="flex items-center gap-2">
      {steps.map((step) => {
        const isCompleted = step < currentStep;
        const isCurrent = step === currentStep;

        return (
          <div key={step} className="flex items-center gap-2">
            <div className="flex flex-col items-center gap-1">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium ${
                  isCurrent
                    ? "bg-[hsl(var(--bloque-primary))] text-[hsl(var(--bloque-primary-foreground))]"
                    : isCompleted
                      ? "bg-green-500 text-white"
                      : "bg-[hsl(var(--bloque-muted))] text-[hsl(var(--bloque-muted-foreground))]"
                }`}
              >
                {isCompleted ? "v" : step + 1}
              </div>
              {stepLabels && stepLabels[step] && (
                <span className="text-xs text-[hsl(var(--bloque-muted-foreground))]">
                  {stepLabels[step]}
                </span>
              )}
            </div>
            {step < totalSteps - 1 && (
              <div
                className={`h-0.5 w-8 ${
                  step < currentStep
                    ? "bg-green-500"
                    : "bg-[hsl(var(--bloque-muted))]"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
