"use client";

import type { FieldProps } from "../types.js";

export type TextFieldProps = FieldProps;

export function TextField({
  name,
  label,
  required = false,
  error,
  value = "",
  onChange,
}: TextFieldProps) {
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
      <input
        id={name}
        name={name}
        type="text"
        value={value}
        required={required}
        onChange={(e) => onChange?.(e.target.value)}
        className={`rounded-md border px-3 py-2 text-sm text-[hsl(var(--bloque-foreground))] bg-[hsl(var(--bloque-background))] placeholder:text-[hsl(var(--bloque-muted-foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--bloque-ring))] ${
          error
            ? "border-red-500"
            : "border-[hsl(var(--bloque-border))]"
        }`}
      />
      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}
    </div>
  );
}
