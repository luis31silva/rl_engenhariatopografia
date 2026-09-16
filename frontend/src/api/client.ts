import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "/api";
const TOKEN_KEY = "rl_token";
const AUTH_LOGOUT_EVENT = "auth:logout";

export const api = axios.create({
  baseURL,
});

// Injeta o token JWT (se existir) em cada pedido.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Em caso de 401 (token inválido/expirado), termina a sessão: limpa o token e
// avisa a app (via evento) para redirecionar para o login. Não recorremos a
// window.location para não perder o estado da SPA; o RequireAuth trata do resto.
api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem(TOKEN_KEY)) {
      localStorage.removeItem(TOKEN_KEY);
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
    }
    return Promise.reject(error);
  },
);
