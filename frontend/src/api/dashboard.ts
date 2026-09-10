import { api } from "./client";

export interface ResumoAno {
  ano: number;
  brutos: string;
  custos: string;
  liquidos: string;
  liquidez_pct: number | null;
  variacao_pct: number | null;
}

export interface LinhaDepreciacao {
  ano: number;
  valor_inicial: string;
  depreciacao: string;
  valor_final: string;
}

export interface DepreciacaoEquipamento {
  equipamento_id: number;
  nome: string;
  linhas: LinhaDepreciacao[];
}

export interface Dashboard {
  resumo_anual: ResumoAno[];
  depreciacao: DepreciacaoEquipamento[];
  total_brutos: string;
  total_custos: string;
  total_liquidos: string;
}

export async function getDashboard(): Promise<Dashboard> {
  const { data } = await api.get<Dashboard>("/dashboard");
  return data;
}

// ---- Custos anuais ----
export interface CustoAnual {
  id: number;
  ano: number;
  valor: string | number;
  descricao?: string | null;
}
export type CustoAnualInput = Omit<CustoAnual, "id">;

export async function listCustos(): Promise<CustoAnual[]> {
  const { data } = await api.get<CustoAnual[]>("/dashboard/custos");
  return data;
}
export async function createCusto(input: CustoAnualInput): Promise<CustoAnual> {
  const { data } = await api.post<CustoAnual>("/dashboard/custos", input);
  return data;
}
export async function updateCusto(id: number, input: Partial<CustoAnualInput>): Promise<CustoAnual> {
  const { data } = await api.put<CustoAnual>(`/dashboard/custos/${id}`, input);
  return data;
}
export async function deleteCusto(id: number): Promise<void> {
  await api.delete(`/dashboard/custos/${id}`);
}

// ---- Equipamentos ----
export interface Equipamento {
  id: number;
  nome: string;
  percentagem: string | number;
  ano_aquisicao: number;
  valor: string | number;
}
export type EquipamentoInput = Omit<Equipamento, "id">;

export async function listEquipamentos(): Promise<Equipamento[]> {
  const { data } = await api.get<Equipamento[]>("/dashboard/equipamentos");
  return data;
}
export async function createEquipamento(input: EquipamentoInput): Promise<Equipamento> {
  const { data } = await api.post<Equipamento>("/dashboard/equipamentos", input);
  return data;
}
export async function updateEquipamento(id: number, input: Partial<EquipamentoInput>): Promise<Equipamento> {
  const { data } = await api.put<Equipamento>(`/dashboard/equipamentos/${id}`, input);
  return data;
}
export async function deleteEquipamento(id: number): Promise<void> {
  await api.delete(`/dashboard/equipamentos/${id}`);
}
