import { describe, it, expect } from "vitest";
import { bloquePreset } from "../preset.js";
import { colors, darkThemeValues, lightThemeValues } from "../theme/colors.js";
import { radius, fontFamily, spacing } from "../theme/tokens.js";

describe("bloquePreset", () => {
  it("has theme.extend.colors", () => {
    expect(bloquePreset.theme?.extend?.colors).toBeDefined();
    const presetColors = bloquePreset.theme!.extend!.colors as Record<string, unknown>;
    expect(presetColors.background).toBe(colors.background);
    expect(presetColors.foreground).toBe(colors.foreground);
  });

  it("has theme.extend.borderRadius", () => {
    const br = bloquePreset.theme!.extend!.borderRadius as Record<string, string>;
    expect(br.lg).toBe(radius.lg);
    expect(br.md).toBe(radius.md);
    expect(br.sm).toBe(radius.sm);
  });

  it("has theme.extend.fontFamily", () => {
    const ff = bloquePreset.theme!.extend!.fontFamily as Record<string, string[]>;
    expect(ff.sans[0]).toBe("Geist");
    expect(ff.mono[0]).toBe("Geist Mono");
  });
});

describe("colors", () => {
  it("all colors reference CSS variables", () => {
    for (const value of Object.values(colors)) {
      expect(value).toMatch(/^hsl\(var\(--bloque-/);
    }
  });
});

describe("theme values", () => {
  it("dark theme has all required variables", () => {
    expect(Object.keys(darkThemeValues).length).toBeGreaterThanOrEqual(15);
    expect(darkThemeValues["--bloque-background"]).toBeDefined();
  });

  it("light theme has all required variables", () => {
    expect(Object.keys(lightThemeValues).length).toBeGreaterThanOrEqual(15);
    expect(lightThemeValues["--bloque-background"]).toBeDefined();
  });
});

describe("design tokens", () => {
  it("radius has standard sizes", () => {
    expect(radius.sm).toBeDefined();
    expect(radius.md).toBeDefined();
    expect(radius.lg).toBeDefined();
    expect(radius.full).toBe("9999px");
  });

  it("fontFamily has sans and mono", () => {
    expect(fontFamily.sans.length).toBeGreaterThan(0);
    expect(fontFamily.mono.length).toBeGreaterThan(0);
  });

  it("spacing has standard values", () => {
    expect(spacing[0]).toBe("0");
    expect(spacing[4]).toBe("1rem");
  });
});
