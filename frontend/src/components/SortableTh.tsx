import { Group, Table, Text, UnstyledButton } from "@mantine/core";
import { IconChevronDown, IconChevronUp, IconSelector } from "@tabler/icons-react";

export type SortDir = "asc" | "desc";

interface Props {
  label: string;
  campo: string;
  sortBy: string | null;
  sortDir: SortDir;
  onSort: (campo: string) => void;
  ta?: "left" | "right" | "center";
  w?: number | string;
}

/** Cabeçalho de coluna clicável para ordenar. */
export function SortableTh({ label, campo, sortBy, sortDir, onSort, ta = "left", w }: Props) {
  const ativo = sortBy === campo;
  const Icon = ativo ? (sortDir === "asc" ? IconChevronUp : IconChevronDown) : IconSelector;

  return (
    <Table.Th w={w}>
      <UnstyledButton onClick={() => onSort(campo)} style={{ width: "100%" }}>
        <Group gap={4} justify={ta === "right" ? "flex-end" : "flex-start"} wrap="nowrap">
          <Text size="sm" fw={600}>
            {label}
          </Text>
          <Icon size={14} style={{ opacity: ativo ? 1 : 0.4 }} />
        </Group>
      </UnstyledButton>
    </Table.Th>
  );
}

/** Ordena uma lista localmente por um campo (com acessor opcional). */
export function ordenarLista<T>(
  lista: T[],
  campo: string | null,
  dir: SortDir,
  acessor?: (item: T, campo: string) => unknown,
): T[] {
  if (!campo) return lista;
  const get = acessor ?? ((item: T, c: string) => (item as unknown as Record<string, unknown>)[c]);
  const copia = [...lista];
  copia.sort((a, b) => {
    const va = get(a, campo);
    const vb = get(b, campo);
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    let r: number;
    if (typeof va === "number" && typeof vb === "number") {
      r = va - vb;
    } else {
      r = String(va).localeCompare(String(vb), "pt", { numeric: true });
    }
    return dir === "asc" ? r : -r;
  });
  return copia;
}
