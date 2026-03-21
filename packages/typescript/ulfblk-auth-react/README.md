# @bloque/auth-react

React hooks, providers, and route guards for the Bloque authentication ecosystem.

## Features

- **Zero external dependencies** - React Context + useReducer only
- **JWT decoder** - Client-side payload reading (server verifies signatures)
- **Cross-stack compatible** - Handles both Python and TypeScript JWT field names
- **RBAC guards** - Mirror Python's permission/role checking semantics

## Installation

```bash
pnpm add @bloque/auth-react @bloque/api-client @bloque/types
```

## Quick Start

```tsx
import { BloqueClient, LocalStorageTokenStorage } from "@bloque/api-client";
import { BloqueProvider, AuthProvider, TenantProvider } from "@bloque/auth-react";

const tokenStorage = new LocalStorageTokenStorage();
const client = new BloqueClient({
  baseUrl: "http://localhost:8000",
  tokenStorage,
});

function App() {
  return (
    <BloqueProvider client={client}>
      <AuthProvider tokenStorage={tokenStorage}>
        <TenantProvider>
          <MyApp />
        </TenantProvider>
      </AuthProvider>
    </BloqueProvider>
  );
}
```

## Hooks

```tsx
import { useAuth, useLogin, useLogout, useTenant, useBloqueClient } from "@bloque/auth-react";

function Dashboard() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const { logout } = useLogout();
  const { tenantId, setTenantId } = useTenant();
  const client = useBloqueClient();

  if (isLoading) return <p>Loading...</p>;
  if (!isAuthenticated) return <p>Not logged in</p>;

  return (
    <div>
      <p>Welcome, {user.userId}</p>
      <p>Tenant: {tenantId}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

function LoginForm() {
  const { login, isLoading, error } = useLogin();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await login("user@example.com", "password");
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <p>{error}</p>}
      <button disabled={isLoading}>Login</button>
    </form>
  );
}
```

## Guards

```tsx
import { RequireAuth, RequireRole, RequirePermission } from "@bloque/auth-react";

// Only render if authenticated
<RequireAuth fallback={<LoginPage />}>
  <Dashboard />
</RequireAuth>

// ANY role match (like Python's require_roles)
<RequireRole roles={["admin", "editor"]} fallback={<AccessDenied />}>
  <AdminPanel />
</RequireRole>

// ALL permissions required, admin bypass (like Python's require_permissions)
<RequirePermission permissions={["users:write", "users:delete"]} fallback={<AccessDenied />}>
  <UserManagement />
</RequirePermission>
```

## Guard Semantics

| Guard | Check | Admin Bypass |
|-------|-------|-------------|
| `RequireAuth` | Is authenticated | N/A |
| `RequireRole` | User has ANY of the listed roles | No |
| `RequirePermission` | User has ALL listed permissions | Yes |

These mirror the Python RBAC behavior in `bloque-auth`.
