import { describe, it, expect } from "vitest";
import { decodeToken, isTokenExpired } from "../jwt-decode.js";

/** Encode a payload to a fake JWT (header.payload.signature) */
function makeToken(payload: Record<string, unknown>): string {
  const header = btoa(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const body = btoa(JSON.stringify(payload))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
  return `${header}.${body}.fake-signature`;
}

describe("decodeToken", () => {
  it("decodes a valid token with TS fields", () => {
    const token = makeToken({
      sub: "user-1",
      tenantId: "tenant-a",
      roles: ["admin"],
      permissions: ["users:read"],
      tokenType: "access",
      exp: 9999999999,
      iat: 1000000000,
    });

    const data = decodeToken(token);
    expect(data.userId).toBe("user-1");
    expect(data.tenantId).toBe("tenant-a");
    expect(data.roles).toEqual(["admin"]);
    expect(data.permissions).toEqual(["users:read"]);
    expect(data.tokenType).toBe("access");
  });

  it("decodes a token with Python fields (tenant, type)", () => {
    const token = makeToken({
      sub: "user-2",
      tenant: "tenant-py",
      type: "refresh",
      roles: ["editor"],
      permissions: [],
    });

    const data = decodeToken(token);
    expect(data.userId).toBe("user-2");
    expect(data.tenantId).toBe("tenant-py");
    expect(data.tokenType).toBe("refresh");
    expect(data.roles).toEqual(["editor"]);
  });

  it("prefers TS fields over Python fields", () => {
    const token = makeToken({
      sub: "user-3",
      tenantId: "ts-tenant",
      tenant: "py-tenant",
      tokenType: "access",
      type: "refresh",
      roles: [],
      permissions: [],
    });

    const data = decodeToken(token);
    expect(data.tenantId).toBe("ts-tenant");
    expect(data.tokenType).toBe("access");
  });

  it("handles missing optional fields gracefully", () => {
    const token = makeToken({ sub: "user-4" });
    const data = decodeToken(token);
    expect(data.userId).toBe("user-4");
    expect(data.tenantId).toBe("");
    expect(data.roles).toEqual([]);
    expect(data.permissions).toEqual([]);
    expect(data.tokenType).toBe("access");
  });

  it("throws on token with fewer than 3 parts", () => {
    expect(() => decodeToken("only.two")).toThrow("Invalid JWT: expected 3 parts");
    expect(() => decodeToken("single")).toThrow("Invalid JWT: expected 3 parts");
    expect(() => decodeToken("")).toThrow("Invalid JWT: expected 3 parts");
  });

  it("throws on invalid base64 payload", () => {
    expect(() => decodeToken("a.!!!.c")).toThrow();
  });

  it("throws on non-JSON payload", () => {
    const notJson = btoa("this is not json");
    expect(() => decodeToken(`a.${notJson}.c`)).toThrow("Invalid JWT: payload is not valid JSON");
  });

  it("throws when sub claim is missing", () => {
    const token = makeToken({ tenantId: "t1", roles: [] });
    expect(() => decodeToken(token)).toThrow("Invalid JWT: missing 'sub' claim");
  });
});

describe("isTokenExpired", () => {
  it("returns false for a token with future exp", () => {
    const token = makeToken({ sub: "u1", exp: Math.floor(Date.now() / 1000) + 3600 });
    expect(isTokenExpired(token)).toBe(false);
  });

  it("returns true for a token with past exp", () => {
    const token = makeToken({ sub: "u1", exp: Math.floor(Date.now() / 1000) - 60 });
    expect(isTokenExpired(token)).toBe(true);
  });

  it("returns false for a token without exp claim", () => {
    const token = makeToken({ sub: "u1" });
    expect(isTokenExpired(token)).toBe(false);
  });

  it("returns true for malformed tokens", () => {
    expect(isTokenExpired("not.a.jwt")).toBe(true);
    expect(isTokenExpired("bad")).toBe(true);
  });
});
