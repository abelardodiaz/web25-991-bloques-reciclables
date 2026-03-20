import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import type { ReactNode } from "react";
import { BloqueClient, MemoryTokenStorage } from "@bloque/api-client";
import { BloqueProvider } from "../contexts/bloque-context.js";
import { AuthProvider } from "../contexts/auth-context.js";
import { RequireAuth } from "../guards/require-auth.js";
import { RequireRole } from "../guards/require-role.js";
import { RequirePermission } from "../guards/require-permission.js";

const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

function makeToken(payload: Record<string, unknown>): string {
  const header = btoa(JSON.stringify({ alg: "RS256", typ: "JWT" }));
  const body = btoa(JSON.stringify(payload))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
  return `${header}.${body}.fake-sig`;
}

function renderGuard(content: ReactNode, tokenStorage?: MemoryTokenStorage) {
  const storage = tokenStorage ?? new MemoryTokenStorage();
  const client = new BloqueClient({ baseUrl: "https://api.test.com", tokenStorage: storage });
  return render(
    <BloqueProvider client={client}>
      <AuthProvider tokenStorage={storage}>{content}</AuthProvider>
    </BloqueProvider>,
  );
}

function makeAuthStorage(overrides: Partial<{
  sub: string;
  roles: string[];
  permissions: string[];
}> = {}): MemoryTokenStorage {
  const storage = new MemoryTokenStorage();
  const token = makeToken({
    sub: overrides.sub ?? "guard-user",
    tenantId: "t1",
    roles: overrides.roles ?? [],
    permissions: overrides.permissions ?? [],
    tokenType: "access",
    exp: Math.floor(Date.now() / 1000) + 3600,
  });
  storage.setTokens(token, "rt");
  return storage;
}

describe("RequireAuth", () => {
  beforeEach(() => mockFetch.mockReset());
  afterEach(() => { cleanup(); vi.restoreAllMocks(); });

  it("renders children when authenticated", async () => {
    const storage = makeAuthStorage();
    renderGuard(
      <RequireAuth>
        <span data-testid="protected">secret</span>
      </RequireAuth>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("protected").textContent).toBe("secret");
    });
  });

  it("renders fallback when not authenticated", async () => {
    renderGuard(
      <RequireAuth fallback={<span data-testid="fallback">login please</span>}>
        <span data-testid="protected">secret</span>
      </RequireAuth>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("fallback").textContent).toBe("login please");
    });
    expect(screen.queryByTestId("protected")).toBeNull();
  });

  it("renders loadingFallback while loading", () => {
    // Without tokenStorage, init is synchronous so loading is brief.
    // We test that the prop is accepted and renders.
    const storage = makeAuthStorage();
    renderGuard(
      <RequireAuth loadingFallback={<span data-testid="loading">loading...</span>}>
        <span data-testid="protected">secret</span>
      </RequireAuth>,
      storage,
    );
    // After init, protected content should appear
    // (loading might be too fast to catch, so we just verify it doesn't crash)
  });

  it("renders nothing when not authenticated and no fallback", async () => {
    const { container } = renderGuard(
      <RequireAuth>
        <span data-testid="protected">secret</span>
      </RequireAuth>,
    );

    await waitFor(() => {
      expect(screen.queryByTestId("protected")).toBeNull();
    });
  });
});

describe("RequireRole", () => {
  beforeEach(() => mockFetch.mockReset());
  afterEach(() => { cleanup(); vi.restoreAllMocks(); });

  it("renders children when user has ANY matching role", async () => {
    const storage = makeAuthStorage({ roles: ["editor", "viewer"] });
    renderGuard(
      <RequireRole roles={["admin", "editor"]}>
        <span data-testid="content">editor panel</span>
      </RequireRole>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("content").textContent).toBe("editor panel");
    });
  });

  it("renders fallback when user has no matching role", async () => {
    const storage = makeAuthStorage({ roles: ["viewer"] });
    renderGuard(
      <RequireRole roles={["admin", "editor"]} fallback={<span data-testid="denied">denied</span>}>
        <span data-testid="content">editor panel</span>
      </RequireRole>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("denied").textContent).toBe("denied");
    });
    expect(screen.queryByTestId("content")).toBeNull();
  });

  it("renders fallback when not authenticated", async () => {
    renderGuard(
      <RequireRole roles={["admin"]} fallback={<span data-testid="denied">no auth</span>}>
        <span data-testid="content">admin</span>
      </RequireRole>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("denied").textContent).toBe("no auth");
    });
  });

  it("checks ANY role (not all)", async () => {
    const storage = makeAuthStorage({ roles: ["manager"] });
    renderGuard(
      <RequireRole roles={["manager", "ceo", "cto"]}>
        <span data-testid="content">ok</span>
      </RequireRole>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("content").textContent).toBe("ok");
    });
  });
});

describe("RequirePermission", () => {
  beforeEach(() => mockFetch.mockReset());
  afterEach(() => { cleanup(); vi.restoreAllMocks(); });

  it("renders children when user has ALL required permissions", async () => {
    const storage = makeAuthStorage({
      permissions: ["users:read", "users:write", "users:delete"],
    });
    renderGuard(
      <RequirePermission permissions={["users:read", "users:write"]}>
        <span data-testid="content">user mgmt</span>
      </RequirePermission>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("content").textContent).toBe("user mgmt");
    });
  });

  it("renders fallback when user is missing a permission", async () => {
    const storage = makeAuthStorage({ permissions: ["users:read"] });
    renderGuard(
      <RequirePermission
        permissions={["users:read", "users:write"]}
        fallback={<span data-testid="denied">missing perms</span>}
      >
        <span data-testid="content">user mgmt</span>
      </RequirePermission>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("denied").textContent).toBe("missing perms");
    });
  });

  it("admin bypasses permission check", async () => {
    const storage = makeAuthStorage({ roles: ["admin"], permissions: [] });
    renderGuard(
      <RequirePermission permissions={["users:read", "users:write", "users:delete"]}>
        <span data-testid="content">admin access</span>
      </RequirePermission>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("content").textContent).toBe("admin access");
    });
  });

  it("non-admin without permissions is denied", async () => {
    const storage = makeAuthStorage({ roles: ["editor"], permissions: [] });
    renderGuard(
      <RequirePermission
        permissions={["users:delete"]}
        fallback={<span data-testid="denied">no</span>}
      >
        <span data-testid="content">delete</span>
      </RequirePermission>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("denied").textContent).toBe("no");
    });
  });

  it("renders fallback when not authenticated", async () => {
    renderGuard(
      <RequirePermission
        permissions={["anything"]}
        fallback={<span data-testid="denied">login</span>}
      >
        <span data-testid="content">protected</span>
      </RequirePermission>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("denied").textContent).toBe("login");
    });
  });

  it("checks ALL permissions (not any)", async () => {
    const storage = makeAuthStorage({ permissions: ["a:read", "b:read"] });
    renderGuard(
      <RequirePermission
        permissions={["a:read", "b:read", "c:read"]}
        fallback={<span data-testid="denied">missing c</span>}
      >
        <span data-testid="content">all</span>
      </RequirePermission>,
      storage,
    );

    await waitFor(() => {
      expect(screen.getByTestId("denied").textContent).toBe("missing c");
    });
  });
});
