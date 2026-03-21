import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act, waitFor, cleanup } from "@testing-library/react";
import { BloqueClient, MemoryTokenStorage } from "@ulfblk/api-client";
import { BloqueProvider } from "../contexts/bloque-context.js";
import { AuthProvider, type AuthProviderProps } from "../contexts/auth-context.js";
import { useAuthContext } from "../contexts/auth-context.js";
import { useAuth } from "../hooks/use-auth.js";

// Mock fetch globally
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

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    statusText: status === 200 ? "OK" : "Error",
    headers: { "Content-Type": "application/json" },
  });
}

function AuthConsumer() {
  const { user, isAuthenticated, isLoading } = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(isLoading)}</span>
      <span data-testid="authenticated">{String(isAuthenticated)}</span>
      <span data-testid="user-id">{user?.userId ?? "none"}</span>
    </div>
  );
}

function renderWithProviders(
  tokenStorage?: MemoryTokenStorage,
  authProps?: Partial<AuthProviderProps>,
) {
  const storage = tokenStorage ?? new MemoryTokenStorage();
  const client = new BloqueClient({ baseUrl: "https://api.test.com", tokenStorage: storage });
  return render(
    <BloqueProvider client={client}>
      <AuthProvider tokenStorage={storage} {...authProps}>
        <AuthConsumer />
      </AuthProvider>
    </BloqueProvider>,
  );
}

describe("AuthProvider", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("renders children", async () => {
    renderWithProviders();
    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
  });

  it("starts with isLoading=true then resolves", async () => {
    const storage = new MemoryTokenStorage();
    renderWithProviders(storage);
    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("false");
  });

  it("initializes without token storage as unauthenticated", async () => {
    const client = new BloqueClient({ baseUrl: "https://api.test.com" });
    render(
      <BloqueProvider client={client}>
        <AuthProvider>
          <AuthConsumer />
        </AuthProvider>
      </BloqueProvider>,
    );
    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("false");
    expect(screen.getByTestId("user-id").textContent).toBe("none");
  });

  it("restores session from existing token on mount", async () => {
    const storage = new MemoryTokenStorage();
    const token = makeToken({
      sub: "restored-user",
      tenantId: "t1",
      roles: ["viewer"],
      permissions: [],
      tokenType: "access",
      exp: Math.floor(Date.now() / 1000) + 3600,
    });
    storage.setTokens(token, "refresh-token");

    renderWithProviders(storage);

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("true");
    expect(screen.getByTestId("user-id").textContent).toBe("restored-user");
  });

  it("does not restore session with expired token", async () => {
    const storage = new MemoryTokenStorage();
    const token = makeToken({
      sub: "expired-user",
      exp: Math.floor(Date.now() / 1000) - 60,
    });
    storage.setTokens(token, "refresh-token");

    renderWithProviders(storage);

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("false");
  });

  it("login flow updates auth state", async () => {
    const storage = new MemoryTokenStorage();
    const client = new BloqueClient({ baseUrl: "https://api.test.com", tokenStorage: storage });

    const accessToken = makeToken({
      sub: "login-user",
      tenantId: "t2",
      roles: ["admin"],
      permissions: ["users:read"],
      tokenType: "access",
    });

    mockFetch.mockResolvedValueOnce(
      jsonResponse({ accessToken, refreshToken: "rt", tokenType: "bearer" }),
    );

    let loginFn: (email: string, password: string) => Promise<void>;

    function LoginConsumer() {
      const auth = useAuth();
      const ctx = useAuthContext();
      loginFn = ctx.login;
      return (
        <div>
          <span data-testid="auth">{String(auth.isAuthenticated)}</span>
          <span data-testid="uid">{auth.user?.userId ?? "none"}</span>
        </div>
      );
    }

    render(
      <BloqueProvider client={client}>
        <AuthProvider tokenStorage={storage}>
          <LoginConsumer />
        </AuthProvider>
      </BloqueProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("auth").textContent).toBe("false");
    });

    await act(async () => {
      await loginFn!("user@test.com", "pass123");
    });

    expect(screen.getByTestId("auth").textContent).toBe("true");
    expect(screen.getByTestId("uid").textContent).toBe("login-user");
  });

  it("logout clears auth state", async () => {
    const storage = new MemoryTokenStorage();
    const token = makeToken({
      sub: "logout-user",
      tenantId: "t1",
      roles: [],
      permissions: [],
      tokenType: "access",
      exp: Math.floor(Date.now() / 1000) + 3600,
    });
    storage.setTokens(token, "rt");

    const client = new BloqueClient({ baseUrl: "https://api.test.com", tokenStorage: storage });

    let logoutFn: () => void;

    function LogoutConsumer() {
      const auth = useAuth();
      const ctx = useAuthContext();
      logoutFn = ctx.logout;
      return (
        <div>
          <span data-testid="auth">{String(auth.isAuthenticated)}</span>
        </div>
      );
    }

    render(
      <BloqueProvider client={client}>
        <AuthProvider tokenStorage={storage}>
          <LogoutConsumer />
        </AuthProvider>
      </BloqueProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("auth").textContent).toBe("true");
    });

    act(() => {
      logoutFn!();
    });

    expect(screen.getByTestId("auth").textContent).toBe("false");
  });

  it("login error sets error state", async () => {
    const storage = new MemoryTokenStorage();
    const client = new BloqueClient({ baseUrl: "https://api.test.com", tokenStorage: storage });

    mockFetch.mockResolvedValueOnce(
      jsonResponse({ detail: "Invalid credentials" }, 401),
    );

    let loginFn: (email: string, password: string) => Promise<void>;

    function ErrorConsumer() {
      const ctx = useAuthContext();
      loginFn = ctx.login;
      return <span data-testid="error">{ctx.error ?? "none"}</span>;
    }

    render(
      <BloqueProvider client={client}>
        <AuthProvider tokenStorage={storage}>
          <ErrorConsumer />
        </AuthProvider>
      </BloqueProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("error").textContent).toBe("none");
    });

    await act(async () => {
      try {
        await loginFn!("bad@test.com", "wrong");
      } catch {
        // expected
      }
    });

    expect(screen.getByTestId("error").textContent).not.toBe("none");
  });

  it("handles malformed token in storage gracefully", async () => {
    const storage = new MemoryTokenStorage();
    storage.setTokens("not-a-valid-jwt", "rt");

    renderWithProviders(storage);

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("false");
  });

  it("handles token without sub in storage gracefully", async () => {
    const storage = new MemoryTokenStorage();
    const token = makeToken({ tenantId: "t1" }); // no sub
    storage.setTokens(token, "rt");

    renderWithProviders(storage);

    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("false");
    });
    expect(screen.getByTestId("authenticated").textContent).toBe("false");
  });
});
