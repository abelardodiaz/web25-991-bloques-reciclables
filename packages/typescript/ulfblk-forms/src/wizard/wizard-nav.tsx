"use client";

import { useWizardContext } from "./wizard-context.js";

export interface WizardNavProps {
  prevLabel?: string;
  nextLabel?: string;
  submitLabel?: string;
  onSubmit?: () => void;
}

export function WizardNav({
  prevLabel = "Anterior",
  nextLabel = "Siguiente",
  submitLabel = "Enviar",
  onSubmit,
}: WizardNavProps) {
  const { goNext, goPrev, isFirst, isLast } = useWizardContext();

  return (
    <div className="flex items-center justify-between pt-4">
      <button
        type="button"
        onClick={goPrev}
        disabled={isFirst}
        className="rounded-md border border-[hsl(var(--bloque-border))] px-4 py-2 text-sm text-[hsl(var(--bloque-foreground))] hover:bg-[hsl(var(--bloque-accent))] disabled:cursor-not-allowed disabled:opacity-50"
      >
        {prevLabel}
      </button>
      {isLast ? (
        <button
          type="button"
          onClick={onSubmit}
          className="rounded-md bg-[hsl(var(--bloque-primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--bloque-primary-foreground))] hover:opacity-90"
        >
          {submitLabel}
        </button>
      ) : (
        <button
          type="button"
          onClick={goNext}
          className="rounded-md bg-[hsl(var(--bloque-primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--bloque-primary-foreground))] hover:opacity-90"
        >
          {nextLabel}
        </button>
      )}
    </div>
  );
}
