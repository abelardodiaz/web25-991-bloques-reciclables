import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { BloqueClient } from "../client.js";
import { BloqueApiError } from "../interceptors/error.js";
import { MemoryTokenStorage, LocalStorageTokenStorage } from "../token-storage.js";

// Mock fetch globally
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    statusText: status === 200 ? "OK" : "Error",
    headers: { "Content-Type": "application/json" },
  });
}

describe("BloqueClient", () => {
  let client: BloqueClient;

  beforeEach(() => {
    mockFetch.mockReset();
    client = new BloqueClient({ baseUrl: "https://api.test.com" });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("HTTP methods", () => {
    it("GET request", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({ id: 1 }));
      const result = await client.get<{ id: number }>("/items/1");
      expect(result).toEqual({ id: 1 });
      expect(mockFetch).toHaveBeenCalledOnce();
      const [url, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      expect(url).toBe("https://api.test.com/items/1");
      expect(init.method).toBe("GET");
    });

    it("POST request with body", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({ id: 2 }));
      const result = await client.post<{ id: number }>("/items", {
        name: "test",
      });
      expect(result).toEqual({ id: 2 });
      const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      expect(init.method).toBe("POST");
      expect(init.body).toBe('{"name":"test"}');
    });

    it("PUT request", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));
      await client.put("/items/1", { name: "updated" });
      const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      expect(init.method).toBe("PUT");
    });

    it("PATCH request", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));
      await client.patch("/items/1", { name: "patched" });
      const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      expect(init.method).toBe("PATCH");
    });

    it("DELETE request", async () => {
      mockFetch.mockResolvedValueOnce(
        new Response(null, { status: 204, statusText: "No Content" }),
      );
      const result = await client.delete("/items/1");
      expect(result).toBeUndefined();
    });
  });

  describe("query params", () => {
    it("appends query params to URL", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({ items: [] }));
      await client.get("/items", { params: { page: "1", size: "10" } });
      const [url] = mockFetch.mock.calls[0] as [string, RequestInit];
      expect(url).toBe("https://api.test.com/items?page=1&size=10");
    });
  });

  describe("auth interceptor", () => {
    it("adds Authorization header when tokens are set", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({}));
      client.setTokens({ accessToken: "my-token", refreshToken: "rt" });
      await client.get("/me");
      const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      const headers = new Headers(init.headers);
      expect(headers.get("Authorization")).toBe("Bearer my-token");
    });

    it("does not add Authorization header without tokens", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({}));
      await client.get("/public");
      const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      const headers = new Headers(init.headers);
      expect(headers.get("Authorization")).toBeNull();
    });
  });

  describe("tenant interceptor", () => {
    it("adds X-Tenant-ID header when tenant is set", async () => {
      mockFetch.mockResolvedValueOnce(jsonResponse({}));
      client.setTenantId("tenant-123");
      await client.get("/data");
      const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      const headers = new Headers(init.headers);
      expect(headers.get("X-Tenant-ID")).toBe("tenant-123");
    });
  });

  describe("error interceptor", () => {
    it("throws BloqueApiError on non-OK response", async () => {
      mockFetch.mockResolvedValueOnce(
        jsonResponse({ detail: "Not found", code: "NOT_FOUND" }, 404),
      );
      await expect(client.get("/missing")).rejects.toThrow(BloqueApiError);
      try {
        await client.get("/missing");
      } catch (err) {
        // second call for assertion detail
      }
    });

    it("BloqueApiError has status and errorResponse", async () => {
      mockFetch.mockResolvedValueOnce(
        jsonResponse({ detail: "Forbidden" }, 403),
      );
      try {
        await client.get("/secret");
        expect.fail("should have thrown");
      } catch (err) {
        const apiErr = err as BloqueApiError;
        expect(apiErr.status).toBe(403);
        expect(apiErr.errorResponse.detail).toBe("Forbidden");
      }
    });
  });

  describe("login/logout", () => {
    it("login stores tokens and returns response", async () => {
      const loginResp = {
        accessToken: "at",
        refreshToken: "rt",
        tokenType: "bearer",
      };
      mockFetch.mockResolvedValueOnce(jsonResponse(loginResp));
      const result = await client.login({
        email: "a@b.com",
        password: "pass",
      });
      expect(result.accessToken).toBe("at");

      // Subsequent request should have the token
      mockFetch.mockResolvedValueOnce(jsonResponse({}));
      await client.get("/me");
      const [, init] = mockFetch.mock.calls[1] as [string, RequestInit];
      const headers = new Headers(init.headers);
      expect(headers.get("Authorization")).toBe("Bearer at");
    });

    it("logout clears tokens", async () => {
      client.setTokens({ accessToken: "at", refreshToken: "rt" });
      client.logout();

      mockFetch.mockResolvedValueOnce(jsonResponse({}));
      await client.get("/public");
      const [, init] = mockFetch.mock.calls[0] as [string, RequestInit];
      const headers = new Headers(init.headers);
      expect(headers.get("Authorization")).toBeNull();
    });
  });

  describe("trailing slash removal", () => {
    it("strips trailing slashes from baseUrl", async () => {
      const c = new BloqueClient({ baseUrl: "https://api.test.com///" });
      mockFetch.mockResolvedValueOnce(jsonResponse({}));
      await c.get("/items");
      const [url] = mockFetch.mock.calls[0] as [string, RequestInit];
      expect(url).toBe("https://api.test.com/items");
    });
  });
});

describe("MemoryTokenStorage", () => {
  it("stores and retrieves tokens", () => {
    const storage = new MemoryTokenStorage();
    expect(storage.getAccessToken()).toBeNull();
    storage.setTokens("at", "rt");
    expect(storage.getAccessToken()).toBe("at");
    expect(storage.getRefreshToken()).toBe("rt");
  });

  it("clear removes tokens", () => {
    const storage = new MemoryTokenStorage();
    storage.setTokens("at", "rt");
    storage.clear();
    expect(storage.getAccessToken()).toBeNull();
    expect(storage.getRefreshToken()).toBeNull();
  });
});
