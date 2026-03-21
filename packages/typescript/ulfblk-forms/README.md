# @ulfblk/forms

React form components - text fields, select, phone, date, and multi-step wizard. Zero external dependencies (only React + Tailwind CSS variables).

## Install

```bash
pnpm add @ulfblk/forms
```

## Quick Start

```tsx
import {
  TextField,
  SelectField,
  FormWizard,
  WizardStep,
  WizardNav,
  WizardProgress,
} from "@ulfblk/forms";

function RegistrationForm() {
  return (
    <FormWizard onComplete={(data) => console.log(data)}>
      <WizardStep title="Datos personales">
        <TextField name="nombre" label="Nombre" required />
        <TextField name="email" label="Correo" required />
        <WizardNav />
      </WizardStep>
      <WizardStep title="Contacto">
        <PhoneField name="telefono" label="Telefono" />
        <SelectField
          name="pais"
          label="Pais"
          options={[
            { value: "mx", label: "Mexico" },
            { value: "ar", label: "Argentina" },
          ]}
        />
        <WizardNav />
      </WizardStep>
    </FormWizard>
  );
}
```

## Components

### Fields

| Component | Description |
|-----------|-------------|
| `TextField` | Label + text input + error message |
| `SelectField` | Label + select dropdown + error message |
| `PhoneField` | Label + tel input + error message |
| `DateField` | Label + date input + error message |

### Wizard

| Component | Description |
|-----------|-------------|
| `FormWizard` | Multi-step container, manages step state |
| `WizardStep` | Single step wrapper with title |
| `WizardNav` | Prev/Next/Submit navigation buttons |
| `WizardProgress` | Step indicators with optional labels |

## Hooks

| Hook | Description |
|------|-------------|
| `useFormWizard(totalSteps)` | Step navigation: currentStep, goNext, goPrev, goTo, isFirst, isLast, data, setField |
| `useWizardContext()` | Access wizard state from within a FormWizard |

## i18n

All text labels are configurable via props with Spanish defaults:

- `placeholderOption` - "Seleccionar..."
- `prevLabel` - "Anterior"
- `nextLabel` - "Siguiente"
- `submitLabel` / `completeBtnLabel` - "Enviar"
