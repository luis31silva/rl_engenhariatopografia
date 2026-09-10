import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { clearToken, getToken, login as loginApi, setToken } from "../api/auth";

interface AuthState {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthCtx = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTok] = useState<string | null>(getToken());

  useEffect(() => {
    // Mantém em sincronia se o token for limpo pelo interceptor (401).
    const onStorage = () => setTok(getToken());
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      isAuthenticated: !!token,
      login: async (username, password) => {
        const t = await loginApi(username, password);
        setToken(t);
        setTok(t);
      },
      logout: () => {
        clearToken();
        setTok(null);
      },
    }),
    [token],
  );

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de AuthProvider.");
  return ctx;
}
