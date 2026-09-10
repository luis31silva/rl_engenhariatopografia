import { api } from "./client";

export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
  database: string;
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>("/health");
  return data;
}
