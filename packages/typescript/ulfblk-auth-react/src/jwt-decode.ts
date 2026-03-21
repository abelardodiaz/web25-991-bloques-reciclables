import type { TokenData } from "@ulfblk/types";

/**
 * Decode a JWT token payload without verifying the signature.
 * Server-side is responsible for signature verification.
 * Handles both Python (tenant, type) and TS (tenantId, tokenType) field names.
 */
export function decodeToken(token: string): TokenData {
  const parts = token.split(".");
  if (parts.length !== 3) {
    throw new Error("Invalid JWT: expected 3 parts");
  }

  const payload = parts[1];
  const json = decodeBase64Url(payload);

  let parsed: Record<string, unknown>;
  try {
    parsed = JSON.parse(json);
  } catch {
    throw new Error("Invalid JWT: payload is not valid JSON");
  }

  const sub = parsed.sub;
  if (typeof sub !== "string") {
    throw new Error("Invalid JWT: missing 'sub' claim");
  }

  // Cross-stack: Python uses "tenant", TS uses "tenantId"
  const tenantId = (parsed.tenantId ?? parsed.tenant ?? "") as string;

  // Cross-stack: Python uses "type", TS uses "tokenType"
  const tokenType = (parsed.tokenType ?? parsed.type ?? "access") as "access" | "refresh";

  const roles = Array.isArray(parsed.roles) ? (parsed.roles as string[]) : [];
  const permissions = Array.isArray(parsed.permissions) ? (parsed.permissions as string[]) : [];

  return {
    userId: sub,
    tenantId,
    roles,
    permissions,
    tokenType,
  };
}

/** Check if a JWT token is expired based on the exp claim */
export function isTokenExpired(token: string): boolean {
  const parts = token.split(".");
  if (parts.length !== 3) return true;

  try {
    const json = decodeBase64Url(parts[1]);
    const parsed = JSON.parse(json) as Record<string, unknown>;
    const exp = parsed.exp;
    if (typeof exp !== "number") return false; // no exp = never expires
    return Date.now() >= exp * 1000;
  } catch {
    return true;
  }
}

function decodeBase64Url(str: string): string {
  // Replace base64url chars with base64
  let base64 = str.replace(/-/g, "+").replace(/_/g, "/");
  // Pad with '='
  const pad = base64.length % 4;
  if (pad === 2) base64 += "==";
  else if (pad === 3) base64 += "=";

  const binary = atob(base64);
  // Handle UTF-8 via percent encoding
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new TextDecoder().decode(bytes);
}
