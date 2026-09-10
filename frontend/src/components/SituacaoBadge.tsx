import { Badge } from "@mantine/core";

import type { Situacao } from "../api/trabalhos";

const cores: Record<Situacao, string> = {
  Pago: "green",
  "Falta pagamento": "orange",
  "Em curso": "yellow",
};

export function SituacaoBadge({ situacao }: { situacao?: Situacao | null }) {
  if (!situacao) return <Badge color="gray" variant="light">—</Badge>;
  return (
    <Badge color={cores[situacao]} variant="filled">
      {situacao}
    </Badge>
  );
}
