# @ulfblk/admin

React Admin DataProvider and AuthProvider for the ulfblk ecosystem.

## Installation

```bash
pnpm add @ulfblk/admin react-admin
```

## Quick Start

```tsx
import { Admin, Resource, ListGuesser, EditGuesser } from "react-admin";
import { BloqueClient } from "@ulfblk/api-client";
import { createDataProvider, createAuthProvider } from "@ulfblk/admin";

const client = new BloqueClient({ baseUrl: "http://localhost:8000" });
const dataProvider = createDataProvider(client);
const authProvider = createAuthProvider(client);

function App() {
  return (
    <Admin dataProvider={dataProvider} authProvider={authProvider}>
      <Resource name="users" list={ListGuesser} edit={EditGuesser} />
      <Resource name="orders" list={ListGuesser} edit={EditGuesser} />
    </Admin>
  );
}
```

## Features

- **DataProvider**: CRUD operations via BloqueClient with FastAPI-compatible query serialization (`qs` with `arrayFormat: 'repeat'`)
- **AuthProvider**: JWT login/logout with client-side token validation via `jwt-decode`
- **Tenant-aware**: BloqueClient's tenant interceptor handles tenant context automatically
- **Configurable**: Custom `basePath`, query serializer, login path
- **Error handling**: Maps HTTP errors to react-admin's `HttpError` (401 -> re-login, 403 -> access denied)
- **Batch operations**: `deleteMany`/`updateMany` execute in batches of 5 to avoid overwhelming the backend

## Options

```tsx
// Custom base path
const dataProvider = createDataProvider(client, { basePath: "/v1" });

// Custom login endpoint
const authProvider = createAuthProvider(client, { loginPath: "/auth/login" });

// Multi-tenant: switch tenants dynamically
client.setTenantId("acme");
// All subsequent requests include tenant context via interceptor
```

## Backend Requirements

The DataProvider expects standard REST endpoints:

| Method | Endpoint | react-admin method |
|--------|----------|-------------------|
| GET | `{basePath}/{resource}` | getList, getMany |
| GET | `{basePath}/{resource}/{id}` | getOne |
| POST | `{basePath}/{resource}` | create |
| PUT | `{basePath}/{resource}/{id}` | update |
| DELETE | `{basePath}/{resource}/{id}` | delete |

List responses must match `PaginatedResponse`:
```json
{ "items": [...], "total": 100 }
```
