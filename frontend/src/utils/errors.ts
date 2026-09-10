import { AxiosError } from "axios";

/** Extrai uma mensagem de erro legível de uma resposta da API. */
export function extractError(e: unknown): string {
  if (e instanceof AxiosError) {
    const detail = e.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      // Erros de validação do Pydantic.
      return detail.map((d: { msg?: string }) => d.msg ?? "").join("; ") || "Dados inválidos.";
    }
    return e.message;
  }
  return "Ocorreu um erro inesperado.";
}
