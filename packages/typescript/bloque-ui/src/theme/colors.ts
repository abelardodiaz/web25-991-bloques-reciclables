/** Bloque color palette as CSS variable references and raw values */

export const colors = {
  background: "hsl(var(--bloque-background))",
  foreground: "hsl(var(--bloque-foreground))",
  card: "hsl(var(--bloque-card))",
  cardForeground: "hsl(var(--bloque-card-foreground))",
  primary: "hsl(var(--bloque-primary))",
  primaryForeground: "hsl(var(--bloque-primary-foreground))",
  secondary: "hsl(var(--bloque-secondary))",
  secondaryForeground: "hsl(var(--bloque-secondary-foreground))",
  muted: "hsl(var(--bloque-muted))",
  mutedForeground: "hsl(var(--bloque-muted-foreground))",
  accent: "hsl(var(--bloque-accent))",
  accentForeground: "hsl(var(--bloque-accent-foreground))",
  destructive: "hsl(var(--bloque-destructive))",
  destructiveForeground: "hsl(var(--bloque-destructive-foreground))",
  border: "hsl(var(--bloque-border))",
  input: "hsl(var(--bloque-input))",
  ring: "hsl(var(--bloque-ring))",
} as const;

/** Raw HSL values for CSS variable definitions (dark theme default) */
export const darkThemeValues = {
  "--bloque-background": "240 10% 3.9%",
  "--bloque-foreground": "0 0% 98%",
  "--bloque-card": "240 10% 3.9%",
  "--bloque-card-foreground": "0 0% 98%",
  "--bloque-primary": "0 0% 98%",
  "--bloque-primary-foreground": "240 5.9% 10%",
  "--bloque-secondary": "240 3.7% 15.9%",
  "--bloque-secondary-foreground": "0 0% 98%",
  "--bloque-muted": "240 3.7% 15.9%",
  "--bloque-muted-foreground": "240 5% 64.9%",
  "--bloque-accent": "240 3.7% 15.9%",
  "--bloque-accent-foreground": "0 0% 98%",
  "--bloque-destructive": "0 62.8% 30.6%",
  "--bloque-destructive-foreground": "0 0% 98%",
  "--bloque-border": "240 3.7% 15.9%",
  "--bloque-input": "240 3.7% 15.9%",
  "--bloque-ring": "240 4.9% 83.9%",
} as const;

/** Raw HSL values for CSS variable definitions (light theme) */
export const lightThemeValues = {
  "--bloque-background": "0 0% 100%",
  "--bloque-foreground": "240 10% 3.9%",
  "--bloque-card": "0 0% 100%",
  "--bloque-card-foreground": "240 10% 3.9%",
  "--bloque-primary": "240 5.9% 10%",
  "--bloque-primary-foreground": "0 0% 98%",
  "--bloque-secondary": "240 4.8% 95.9%",
  "--bloque-secondary-foreground": "240 5.9% 10%",
  "--bloque-muted": "240 4.8% 95.9%",
  "--bloque-muted-foreground": "240 3.8% 46.1%",
  "--bloque-accent": "240 4.8% 95.9%",
  "--bloque-accent-foreground": "240 5.9% 10%",
  "--bloque-destructive": "0 84.2% 60.2%",
  "--bloque-destructive-foreground": "0 0% 98%",
  "--bloque-border": "240 5.9% 90%",
  "--bloque-input": "240 5.9% 90%",
  "--bloque-ring": "240 5.9% 10%",
} as const;
