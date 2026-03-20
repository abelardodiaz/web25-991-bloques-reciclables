import { useAuthContext } from "../contexts/auth-context.js";

export interface UseLogoutReturn {
  logout: () => void;
}

/** Returns a logout function */
export function useLogout(): UseLogoutReturn {
  const { logout } = useAuthContext();
  return { logout };
}
