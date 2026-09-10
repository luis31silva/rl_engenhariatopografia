import { api } from "./client";

export interface Especialidade {
  id: number;
  codigo: string;
  descricao?: string | null;
  prazo_top: number;
  prazo_ok: number;
}
export type EspecialidadeInput = Omit<Especialidade, "id">;

export interface Intermediario {
  id: number;
  nome: string;
  valor?: string | number | null;
  num_trabalhos?: number;
  valor_total?: string | number;
  valor_medio?: string | number;
  num_trabalhos_ano?: number;
  valor_ano?: string | number;
}
export type IntermediarioInput = Omit<Intermediario, "id">;

export interface Externo {
  id: number;
  nome: string;
  total_ganho?: string | number;
  num_trabalhos?: number;
}
// No input só o nome é editável; as estatísticas são calculadas no servidor.
export type ExternoInput = { nome: string };

// ---- Especialidades ----
export async function listEspecialidades(): Promise<Especialidade[]> {
  const { data } = await api.get<Especialidade[]>("/especialidades");
  return data;
}
export async function createEspecialidade(input: EspecialidadeInput): Promise<Especialidade> {
  const { data } = await api.post<Especialidade>("/especialidades", input);
  return data;
}
export async function updateEspecialidade(id: number, input: Partial<EspecialidadeInput>): Promise<Especialidade> {
  const { data } = await api.put<Especialidade>(`/especialidades/${id}`, input);
  return data;
}
export async function deleteEspecialidade(id: number): Promise<void> {
  await api.delete(`/especialidades/${id}`);
}

// ---- Intermediários ----
export async function listIntermediarios(): Promise<Intermediario[]> {
  const { data } = await api.get<Intermediario[]>("/intermediarios");
  return data;
}
export async function createIntermediario(input: IntermediarioInput): Promise<Intermediario> {
  const { data } = await api.post<Intermediario>("/intermediarios", input);
  return data;
}
export async function updateIntermediario(id: number, input: Partial<IntermediarioInput>): Promise<Intermediario> {
  const { data } = await api.put<Intermediario>(`/intermediarios/${id}`, input);
  return data;
}
export async function deleteIntermediario(id: number): Promise<void> {
  await api.delete(`/intermediarios/${id}`);
}

// ---- Externos ----
export async function listExternos(): Promise<Externo[]> {
  const { data } = await api.get<Externo[]>("/externos");
  return data;
}
export async function createExterno(input: ExternoInput): Promise<Externo> {
  const { data } = await api.post<Externo>("/externos", input);
  return data;
}
export async function updateExterno(id: number, input: Partial<ExternoInput>): Promise<Externo> {
  const { data } = await api.put<Externo>(`/externos/${id}`, input);
  return data;
}
export async function deleteExterno(id: number): Promise<void> {
  await api.delete(`/externos/${id}`);
}
