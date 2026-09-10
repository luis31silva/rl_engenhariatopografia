import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export const api = axios.create({
  baseURL,
});

// Injeta o token JWT (se existir) em cada pedido.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("rl_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Em caso de 401, limpa o token e redireciona para o login.
api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("rl_token");
      // Evita redirecionar quando já estamos no login.
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);
