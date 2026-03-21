"use client";

import type { FieldProps } from "../types.js";

export interface SelectOption {
  value: string;
  label: string;
}

export interface SelectFieldProps extends FieldProps {
  options: SelectOption[];
  placeholderOption?: string;
}

export function SelectField({
  name,
  label,
  required = false,
  error,
  value = "",
  onChange,
  options,
  placeholderOption = "Seleccionar...",
}: SelectFieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label
        htmlFor={name}
        className="text-sm font-medium text-[hsl(var(--bloque-foreground))]"
      >
        {label}
        {required && (
          <span className="ml-0.5 text-red-500">*</span>
        )}
      </label>
      <select
        id={name}
        name={name}
        value={value}
        required={required}
        onChange={(e) => onChange?.(e.target.value)}
        className={`rounded-md border px-3 py-2 text-sm text-[hsl(var(--bloque-foreground))] bg-[hsl(var(--bloque-background))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--bloque-ring))] ${
          error
            ? "border-red-500"
            : "border-[hsl(var(--bloque-border))]"
        }`}
      >
        <option value="">{placeholderOption}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}
    </div>
  );
}
