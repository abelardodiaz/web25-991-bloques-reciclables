# @bloque/api-client

HTTP API client for the Bloque ecosystem. Zero external dependencies — uses native `fetch` (browser + Node 18+ + Deno + Bun).

## Install

```bash
pnpm add @bloque/api-client
```

## Usage

```typescript
import { BloqueClient } from "@bloque/api-client";

const client = new BloqueClient({
  baseUrl: "https://api.example.com",
});

// Login (stores tokens automatically)
await client.login({ email: "user@example.com", password: "secret" });

// Set tenant for multitenant APIs
client.setTenantId("tenant-123");

// CRUD
const items = await client.get<Item[]>("/items");
const created = await client.post<Item>("/items", { name: "New" });
await client.put("/items/1", { name: "Updated" });
await client.patch("/items/1", { name: "Patched" });
await client.delete("/items/1");

// Query params
const page = await client.get("/items", { params: { page: "1", size: "10" } });

// Logout (clears tokens)
client.logout();
```

## Features

- **Auth interceptor**: Adds `Authorization: Bearer <token>` automatically when tokens are set
- **Tenant interceptor**: Adds `X-Tenant-ID` header when tenant is set
- **Error interceptor**: Non-OK responses throw `BloqueApiError` with status and parsed error body
- **Token storage**: `MemoryTokenStorage` (default) or `LocalStorageTokenStorage` (browser)
- **Custom interceptors**: Add your own request/response interceptors

## Token Storage

```typescript
import { BloqueClient, LocalStorageTokenStorage } from "@bloque/api-client";

// Browser: persist tokens in localStorage
const client = new BloqueClient({
  baseUrl: "https://api.example.com",
  tokenStorage: new LocalStorageTokenStorage("myapp"),
});

// Tokens survive page refresh
client.setTokens({ accessToken: "at", refreshToken: "rt" });
```

## Error Handling

```typescript
import { BloqueApiError } from "@bloque/api-client";

try {
  await client.get("/secret");
} catch (err) {
  if (err instanceof BloqueApiError) {
    console.log(err.status);              // 403
    console.log(err.errorResponse.detail); // "Forbidden"
    console.log(err.errorResponse.code);   // "FORBIDDEN"
  }
}
```

## Custom Interceptors

```typescript
// Log all requests
client.addRequestInterceptor((url, init) => {
  console.log(`${init.method} ${url}`);
  return init;
});

// Log response times
client.addResponseInterceptor(async (response) => {
  console.log(`${response.status} ${response.url}`);
  return response;
});
```

## License

MIT
