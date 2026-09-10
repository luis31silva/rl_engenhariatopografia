import { Badge } from "@mantine/core";

import type { Estado } from "../api/trabalhos";

const cores: Record<Estado, string> = {
  TOP: "green",
  OK: "blue",
  MAU: "red",
  PENDENTE: "gray",
};

export function EstadoBadge({ estado }: { estado?: Estado | null }) {
  if (!estado) return <Badge color="gray" variant="light">—</Badge>;
  return (
    <Badge color={cores[estado]} variant="light">
      {estado}
    </Badge>
  );
}
