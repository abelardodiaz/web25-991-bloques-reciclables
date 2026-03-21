import type { TokenData } from "@ulfblk/types";
import { useAuthContext } from "../contexts/auth-context.js";

export interface UseAuthReturn {
  user: TokenData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

/** Returns the current authentication state */
export function useAuth(): UseAuthReturn {
  const { user, isAuthenticated, isLoading } = useAuthContext();
  return { user, isAuthenticated, isLoading };
}
