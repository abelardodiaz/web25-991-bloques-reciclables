import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TextField } from "../fields/text-field.js";
import { SelectField } from "../fields/select-field.js";
import { PhoneField } from "../fields/phone-field.js";
import { DateField } from "../fields/date-field.js";

describe("TextField", () => {
  it("renders label", () => {
    render(<TextField name="email" label="Correo" />);
    expect(screen.getByText("Correo")).toBeDefined();
  });

  it("renders required indicator", () => {
    render(<TextField name="email" label="Correo" required />);
    expect(screen.getByText("*")).toBeDefined();
  });

  it("renders error message", () => {
    render(
      <TextField name="email" label="Correo" error="Campo obligatorio" />,
    );
    expect(screen.getByText("Campo obligatorio")).toBeDefined();
  });

  it("calls onChange when typing", () => {
    const onChange = vi.fn();
    render(<TextField name="email" label="Correo" onChange={onChange} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "test@mail.com" } });
    expect(onChange).toHaveBeenCalledWith("test@mail.com");
  });
});

describe("SelectField", () => {
  it("renders options", () => {
    render(
      <SelectField
        name="country"
        label="Pais"
        options={[
          { value: "mx", label: "Mexico" },
          { value: "ar", label: "Argentina" },
        ]}
      />,
    );
    expect(screen.getByText("Mexico")).toBeDefined();
    expect(screen.getByText("Argentina")).toBeDefined();
  });
});

describe("PhoneField", () => {
  it("renders with tel type", () => {
    render(<PhoneField name="phone" label="Telefono" />);
    const input = document.querySelector('input[type="tel"]');
    expect(input).toBeDefined();
  });
});

describe("DateField", () => {
  it("renders with date type", () => {
    render(<DateField name="birthdate" label="Fecha" />);
    const input = document.querySelector('input[type="date"]');
    expect(input).toBeDefined();
  });
});
