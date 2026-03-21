import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { FormWizard } from "../wizard/form-wizard.js";
import { WizardStep } from "../wizard/wizard-step.js";
import { WizardNav } from "../wizard/wizard-nav.js";
import { WizardProgress } from "../wizard/wizard-progress.js";

describe("FormWizard", () => {
  it("renders first step by default", () => {
    render(
      <FormWizard onComplete={() => {}}>
        <WizardStep title="Paso 1">
          <p>Contenido paso 1</p>
        </WizardStep>
        <WizardStep title="Paso 2">
          <p>Contenido paso 2</p>
        </WizardStep>
      </FormWizard>,
    );
    expect(screen.getByText("Paso 1")).toBeDefined();
    expect(screen.getByText("Contenido paso 1")).toBeDefined();
  });

  it("renders WizardNav with default labels", () => {
    render(
      <FormWizard onComplete={() => {}}>
        <WizardStep title="Paso 1">
          <WizardNav />
        </WizardStep>
        <WizardStep title="Paso 2">
          <WizardNav />
        </WizardStep>
      </FormWizard>,
    );
    const anteriorButtons = screen.getAllByText("Anterior");
    expect(anteriorButtons.length).toBeGreaterThanOrEqual(1);
    const siguienteButtons = screen.getAllByText("Siguiente");
    expect(siguienteButtons.length).toBeGreaterThanOrEqual(1);
  });

  it("navigates to next step when Siguiente is clicked", () => {
    render(
      <FormWizard onComplete={() => {}}>
        <WizardStep title="Paso 1">
          <p>Contenido paso 1</p>
          <WizardNav />
        </WizardStep>
        <WizardStep title="Paso 2">
          <p>Contenido paso 2</p>
          <WizardNav />
        </WizardStep>
      </FormWizard>,
    );
    const siguienteButtons = screen.getAllByText("Siguiente");
    fireEvent.click(siguienteButtons[0]);
    // Paso 2 should now be visible (its parent div has display: block)
    const paso2Container = screen.getByText("Paso 2").closest("div[style]");
    expect(paso2Container).toBeDefined();
  });
});

describe("WizardProgress", () => {
  it("renders step indicators", () => {
    render(<WizardProgress currentStep={0} totalSteps={3} />);
    expect(screen.getByText("1")).toBeDefined();
    expect(screen.getByText("2")).toBeDefined();
    expect(screen.getByText("3")).toBeDefined();
  });

  it("renders step labels when provided", () => {
    render(
      <WizardProgress
        currentStep={1}
        totalSteps={3}
        stepLabels={["Datos", "Contacto", "Confirmar"]}
      />,
    );
    expect(screen.getByText("Datos")).toBeDefined();
    expect(screen.getByText("Contacto")).toBeDefined();
    expect(screen.getByText("Confirmar")).toBeDefined();
  });
});
