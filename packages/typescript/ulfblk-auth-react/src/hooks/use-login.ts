import { useCallback, useState } from "react";
import { useAuthContext } from "../contexts/auth-context.js";

export interface UseLoginReturn {
  login: (email: string, password: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

/** Returns a login function with loading and error state */
export function useLogin(): UseLoginReturn {
  const { login: contextLogin } = useAuthContext();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true);
      setError(null);
      try {
        await contextLogin(email, password);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        setError(message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [contextLogin],
  );

  return { login, isLoading, error };
}
