# @bloque/ui

Tailwind CSS preset and utilities for the Bloque design system. This is NOT a component library — use shadcn/ui via Copier templates for components.

## Install

```bash
pnpm add @bloque/ui
```

## Usage

### cn() utility

Merge Tailwind CSS classes without conflicts (clsx + tailwind-merge):

```typescript
import { cn } from "@bloque/ui";

cn("px-4", "px-2");                    // "px-2"
cn("text-red-500", "text-blue-500");   // "text-blue-500"
cn("base", isActive && "active");      // "base active" or "base"
cn({ hidden: !visible, flex: visible }); // conditional object syntax
```

### Tailwind Preset

Add the Bloque design system to your Tailwind config:

```javascript
// tailwind.config.js
import { bloquePreset } from "@bloque/ui";

export default {
  presets: [bloquePreset],
  // your config...
};
```

The preset provides:
- **Colors**: background, foreground, primary, secondary, muted, accent, destructive, border, input, ring (via CSS variables)
- **Border radius**: sm, md, lg
- **Font family**: Geist Sans + Geist Mono

### CSS Variables

Set up theme variables in your global CSS:

```typescript
import { darkThemeValues, lightThemeValues } from "@bloque/ui";

// Use in CSS-in-JS or generate a stylesheet
// darkThemeValues = { "--bloque-background": "240 10% 3.9%", ... }
// lightThemeValues = { "--bloque-background": "0 0% 100%", ... }
```

### Design Tokens

Access raw design tokens for custom usage:

```typescript
import { colors, radius, fontFamily, spacing } from "@bloque/ui";

// colors.primary = "hsl(var(--bloque-primary))"
// radius.lg = "0.5rem"
// fontFamily.sans = ["Geist", "ui-sans-serif", ...]
// spacing[4] = "1rem"
```

## Philosophy

`@bloque/ui` provides the foundation (theme, tokens, utilities). Actual UI components come from shadcn/ui installed via Copier templates into your project — because shadcn components are source code you own and customize, not a published package.

## License

MIT
