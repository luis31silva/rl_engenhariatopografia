import { api } from "./client";

const TOKEN_KEY = "rl_token";
// Evento disparado quando a sessão termina (logout manual ou token inválido/expirado).
export const AUTH_LOGOUT_EVENT = "auth:logout";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  // Notifica a app (no mesmo separador) para atualizar o estado de autenticação.
  window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
}

export async function login(username: string, password: string): Promise<string> {
  // O endpoint usa OAuth2PasswordRequestForm (form-urlencoded).
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);
  const { data } = await api.post<{ access_token: string }>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data.access_token;
}

export async function me(): Promise<{ username: string }> {
  const { data } = await api.get<{ username: string }>("/auth/me");
  return data;
}
