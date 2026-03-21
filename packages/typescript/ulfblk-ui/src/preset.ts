import type { Config } from "tailwindcss";
import { colors } from "./theme/colors.js";
import { fontFamily, radius } from "./theme/tokens.js";

/** Tailwind CSS preset for the Bloque design system */
export const bloquePreset: Partial<Config> = {
  theme: {
    extend: {
      colors: {
        background: colors.background,
        foreground: colors.foreground,
        card: {
          DEFAULT: colors.card,
          foreground: colors.cardForeground,
        },
        primary: {
          DEFAULT: colors.primary,
          foreground: colors.primaryForeground,
        },
        secondary: {
          DEFAULT: colors.secondary,
          foreground: colors.secondaryForeground,
        },
        muted: {
          DEFAULT: colors.muted,
          foreground: colors.mutedForeground,
        },
        accent: {
          DEFAULT: colors.accent,
          foreground: colors.accentForeground,
        },
        destructive: {
          DEFAULT: colors.destructive,
          foreground: colors.destructiveForeground,
        },
        border: colors.border,
        input: colors.input,
        ring: colors.ring,
      },
      borderRadius: {
        lg: radius.lg,
        md: radius.md,
        sm: radius.sm,
      },
      fontFamily: {
        sans: [...fontFamily.sans],
        mono: [...fontFamily.mono],
      },
    },
  },
};
