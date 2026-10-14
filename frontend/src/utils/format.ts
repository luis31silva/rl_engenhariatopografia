/** Formata um valor monetário em euros (pt-PT). */
export function eur(v: string | number | null | undefined): string {
  if (v == null || v === "") return "—";
  const n = typeof v === "string" ? Number(v) : v;
  if (Number.isNaN(n)) return "—";
  return n.toLocaleString("pt-PT", { style: "currency", currency: "EUR" });
}

const MESES = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
];

/** Nome do mês (1..12) em português. */
export function nomeMes(mes: number): string {
  return MESES[mes - 1] ?? String(mes);
}

/** Abreviatura do mês (1..12) em português, ex.: "Jan". */
export function nomeMesCurto(mes: number): string {
  const nome = MESES[mes - 1];
  return nome ? nome.slice(0, 3) : String(mes);
}
