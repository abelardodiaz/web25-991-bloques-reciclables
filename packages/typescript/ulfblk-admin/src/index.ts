/**
 * @ulfblk/admin - React Admin providers for the ulfblk ecosystem.
 *
 * Provides DataProvider and AuthProvider that use BloqueClient
 * as the HTTP transport layer, with automatic tenant context,
 * JWT auth, and FastAPI-compatible query serialization.
 */

export { createDataProvider } from "./data-provider.js";
export { createAuthProvider } from "./auth-provider.js";
export type { DataProviderOptions, AuthProviderOptions, ListResponse } from "./types.js";
