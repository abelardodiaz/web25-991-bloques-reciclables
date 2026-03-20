import { createContext, useContext, useReducer, useEffect, useCallback, createElement } from "react";
import type { ReactNode } from "react";
import type { TokenData } from "@bloque/types";
import type { TokenStorage } from "@bloque/api-client";
import { useBloqueContext } from "./bloque-context.js";
import { decodeToken, isTokenExpired } from "../jwt-decode.js";

// --- State ---

export interface AuthState {
  user: TokenData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// --- Actions ---

type AuthAction =
  | { type: "LOGIN_START" }
  | { type: "LOGIN_SUCCESS"; user: TokenData }
  | { type: "LOGIN_ERROR"; error: string }
  | { type: "LOGOUT" }
  | { type: "INIT_COMPLETE"; user: TokenData | null };

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "LOGIN_START":
      return { ...state, isLoading: true, error: null };
    case "LOGIN_SUCCESS":
      return { user: action.user, isAuthenticated: true, isLoading: false, error: null };
    case "LOGIN_ERROR":
      return { user: null, isAuthenticated: false, isLoading: false, error: action.error };
    case "LOGOUT":
      return { user: null, isAuthenticated: false, isLoading: false, error: null };
    case "INIT_COMPLETE":
      return {
        user: action.user,
        isAuthenticated: action.user !== null,
        isLoading: false,
        error: null,
      };
  }
}

// --- Context ---

export interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export interface AuthProviderProps {
  children: ReactNode;
  tokenStorage?: TokenStorage;
}

export function AuthProvider({ children, tokenStorage }: AuthProviderProps) {
  const client = useBloqueContext();
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Restore session on mount
  useEffect(() => {
    if (!tokenStorage) {
      dispatch({ type: "INIT_COMPLETE", user: null });
      return;
    }

    const accessToken = tokenStorage.getAccessToken();
    if (accessToken && !isTokenExpired(accessToken)) {
      try {
        const user = decodeToken(accessToken);
        dispatch({ type: "INIT_COMPLETE", user });
      } catch {
        dispatch({ type: "INIT_COMPLETE", user: null });
      }
    } else {
      dispatch({ type: "INIT_COMPLETE", user: null });
    }
  }, [tokenStorage]);

  const login = useCallback(
    async (email: string, password: string) => {
      dispatch({ type: "LOGIN_START" });
      try {
        const response = await client.login({ email, password });
        const user = decodeToken(response.accessToken);
        dispatch({ type: "LOGIN_SUCCESS", user });
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        dispatch({ type: "LOGIN_ERROR", error: message });
        throw err;
      }
    },
    [client],
  );

  const logout = useCallback(() => {
    client.logout();
    dispatch({ type: "LOGOUT" });
  }, [client]);

  const value: AuthContextValue = {
    ...state,
    login,
    logout,
  };

  return createElement(AuthContext.Provider, { value }, children);
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return ctx;
}
