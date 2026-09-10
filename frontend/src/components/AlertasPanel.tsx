import { useQuery } from "@tanstack/react-query";
import { Alert, Badge, Group, Stack, Text } from "@mantine/core";
import { IconAlertTriangle } from "@tabler/icons-react";

import { listAlertas, type TrabalhoAlerta } from "../api/trabalhos";

function descricaoDias(a: TrabalhoAlerta): string {
  if (a.dias_restantes < 0) {
    const dias = Math.abs(a.dias_restantes);
    return `${dias} dia(s) em atraso`;
  }
  if (a.dias_restantes === 0) return "termina hoje";
  return `faltam ${a.dias_restantes} dia(s)`;
}

export function AlertasPanel() {
  const { data = [] } = useQuery({
    queryKey: ["alertas"],
    queryFn: listAlertas,
    refetchInterval: 60_000,
  });

  if (data.length === 0) return null;

  const ultrapassados = data.filter((a) => a.nivel === "ULTRAPASSADO").length;

  return (
    <Alert
      variant="light"
      color={ultrapassados > 0 ? "red" : "orange"}
      icon={<IconAlertTriangle size={18} />}
      title={`Prazos a vencer (${data.length})`}
    >
      <Stack gap={6}>
        {data.slice(0, 6).map((a) => (
          <Group key={a.item_id} justify="space-between" wrap="nowrap">
            <Text size="sm" truncate>
              {a.referencia ? `${a.referencia} — ` : ""}
              {a.cliente ?? "(sem cliente)"}
              {a.especialidade_codigo ? ` · ${a.especialidade_codigo}` : ""}
            </Text>
            <Badge color={a.nivel === "ULTRAPASSADO" ? "red" : "orange"} variant="filled">
              {descricaoDias(a)}
            </Badge>
          </Group>
        ))}
        {data.length > 6 && (
          <Text size="xs" c="dimmed">
            e mais {data.length - 6}…
          </Text>
        )}
      </Stack>
    </Alert>
  );
}
