import { useBloqueContext } from "../contexts/bloque-context.js";
import type { BloqueClient } from "@ulfblk/api-client";

/** Returns the BloqueClient instance from the nearest BloqueProvider */
export function useBloqueClient(): BloqueClient {
  return useBloqueContext();
}
