import { createContext, useContext, createElement } from "react";
import type { ReactNode } from "react";
import type { BloqueClient } from "@ulfblk/api-client";

const BloqueContext = createContext<BloqueClient | null>(null);

export interface BloqueProviderProps {
  client: BloqueClient;
  children: ReactNode;
}

export function BloqueProvider({ client, children }: BloqueProviderProps) {
  return createElement(BloqueContext.Provider, { value: client }, children);
}

export function useBloqueContext(): BloqueClient {
  const client = useContext(BloqueContext);
  if (!client) {
    throw new Error("useBloqueContext must be used within a BloqueProvider");
  }
  return client;
}
