import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { AUTH_LOGOUT_EVENT, clearToken, getToken, login as loginApi, setToken } from "../api/auth";

interface AuthState {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthCtx = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTok] = useState<string | null>(getToken());

  useEffect(() => {
    // Sincroniza o estado quando o token muda:
    // - `storage`: alterações noutro separador.
    // - `auth:logout`: token limpo neste separador (ex.: 401 no interceptor).
    const sincronizar = () => setTok(getToken());
    window.addEventListener("storage", sincronizar);
    window.addEventListener(AUTH_LOGOUT_EVENT, sincronizar);
    return () => {
      window.removeEventListener("storage", sincronizar);
      window.removeEventListener(AUTH_LOGOUT_EVENT, sincronizar);
    };
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
