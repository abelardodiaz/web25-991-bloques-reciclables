export interface FieldProps {
  name: string;
  label: string;
  required?: boolean;
  error?: string;
  value?: string;
  onChange?: (value: string) => void;
}

export interface WizardState {
  currentStep: number;
  totalSteps: number;
  data: Record<string, unknown>;
}
