import { api } from "./client";

export type Estado = "TOP" | "OK" | "MAU" | "PENDENTE";

export type Situacao = "Em curso" | "Falta pagamento" | "Pago";
export const SITUACOES: Situacao[] = ["Em curso", "Falta pagamento", "Pago"];

export interface TrabalhoItem {
  id?: number;
  especialidade_id?: number | null;
  externo_id?: number | null;
  valor?: string | number | null;
  valor_externo?: string | number | null;
  data_adjudicacao?: string | null;
  data_entrega?: string | null;
  situacao?: Situacao | null;
  observacoes?: string | null;
  // Campos de leitura (calculados no servidor).
  especialidade_codigo?: string | null;
  externo_nome?: string | null;
  estado?: Estado | null;
}

export interface Trabalho {
  id: number;
  referencia?: string | null;
  cliente?: string | null;
  contacto?: string | null;
  localidade?: string | null;
  endereco?: string | null;
  intermediario_id?: number | null;
  observacoes?: string | null;
  intermediario_nome?: string | null;
  itens: TrabalhoItem[];
  valor_total?: string | number;
  valor_externo_total?: string | number;
  situacao_trabalho?: Situacao | null;
}

export interface TrabalhoItemInput {
  especialidade_id?: number | null;
  externo_id?: number | null;
  valor?: string | number | null;
  valor_externo?: string | number | null;
  data_adjudicacao?: string | null;
  data_entrega?: string | null;
  situacao?: Situacao | null;
  observacoes?: string | null;
}

export interface TrabalhoInput {
  referencia?: string | null;
  cliente?: string | null;
  contacto?: string | null;
  localidade?: string | null;
  endereco?: string | null;
  intermediario_id?: number | null;
  observacoes?: string | null;
  itens: TrabalhoItemInput[];
  // Se fornecido no update, aplica esta situação a todas as especialidades.
  situacao_todos?: Situacao | null;
}

export interface TrabalhoPage {
  items: Trabalho[];
  total: number;
  page: number;
  page_size: number;
}

export interface TrabalhoFiltros {
  q?: string;
  especialidade_id?: number | null;
  intermediario_id?: number | null;
  externo_id?: number | null;
  ano?: number | null;
  estado?: Estado | null;
  order_by?: string;
  order_dir?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export async function listTrabalhos(filtros: TrabalhoFiltros = {}): Promise<TrabalhoPage> {
  const params: Record<string, string | number> = {};
  for (const [k, v] of Object.entries(filtros)) {
    if (v !== undefined && v !== null && v !== "") params[k] = v as string | number;
  }
  const { data } = await api.get<TrabalhoPage>("/trabalhos", { params });
  return data;
}

export async function getTrabalho(id: number): Promise<Trabalho> {
  const { data } = await api.get<Trabalho>(`/trabalhos/${id}`);
  return data;
}

export async function getProximaReferencia(): Promise<string> {
  const { data } = await api.get<{ referencia: string }>("/trabalhos/proxima-referencia");
  return data.referencia;
}

export async function createTrabalho(input: TrabalhoInput): Promise<Trabalho> {
  const { data } = await api.post<Trabalho>("/trabalhos", input);
  return data;
}

export async function updateTrabalho(id: number, input: Partial<TrabalhoInput>): Promise<Trabalho> {
  const { data } = await api.put<Trabalho>(`/trabalhos/${id}`, input);
  return data;
}

export async function deleteTrabalho(id: number): Promise<void> {
  await api.delete(`/trabalhos/${id}`);
}

export type NivelAlerta = "EM_RISCO" | "ULTRAPASSADO";

export interface TrabalhoAlerta {
  trabalho_id: number;
  item_id: number;
  referencia: string | null;
  cliente: string | null;
  especialidade_codigo: string | null;
  data_adjudicacao: string | null;
  prazo_ok: number | null;
  dias_restantes: number;
  nivel: NivelAlerta;
}

export async function listAlertas(): Promise<TrabalhoAlerta[]> {
  const { data } = await api.get<TrabalhoAlerta[]>("/trabalhos/alertas");
  return data;
}

export async function downloadFatura(id: number, referencia?: string | null): Promise<void> {
  const resp = await api.get(`/trabalhos/${id}/fatura`, { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([resp.data], { type: "application/pdf" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = `recibo-${(referencia || id).toString().replace(/[/\s]/g, "-")}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
