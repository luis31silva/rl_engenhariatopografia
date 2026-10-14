import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Collapse,
  Group,
  Loader,
  Paper,
  Stack,
  Table,
  Text,
  Title,
  UnstyledButton,
} from "@mantine/core";
import { IconChevronDown, IconChevronRight } from "@tabler/icons-react";

import { getDashboard } from "../api/dashboard";
import { GestaoCustos } from "../components/GestaoCustos";
import { GestaoEquipamentos } from "../components/GestaoEquipamentos";
import { eur } from "../utils/format";

export function EquipamentosPage() {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: getDashboard });
  const [depreciacaoAberta, setDepreciacaoAberta] = useState(false);

  const anoAtual = new Date().getFullYear();

  return (
    <Stack>
      <Title order={2}>Equipamentos</Title>

      {/* Custos anuais primeiro, conforme pedido. */}
      <GestaoCustos />

      <GestaoEquipamentos />

      {isLoading && (
        <Group justify="center" mt="md">
          <Loader />
        </Group>
      )}

      {data && data.depreciacao.length > 0 && (
        <Paper withBorder radius="md" p="md">
          <UnstyledButton
            onClick={() => setDepreciacaoAberta((v) => !v)}
            style={{ width: "100%" }}
          >
            <Group justify="space-between">
              <Title order={4}>Previsão de depreciação de equipamento</Title>
              {depreciacaoAberta ? (
                <IconChevronDown size={20} />
              ) : (
                <IconChevronRight size={20} />
              )}
            </Group>
          </UnstyledButton>

          <Collapse in={depreciacaoAberta}>
            <Stack gap="lg" mt="md">
              {data.depreciacao.map((eq) => (
                <div key={eq.equipamento_id}>
                  <Text fw={500} mb={4}>
                    {eq.nome}
                  </Text>
                  <Table.ScrollContainer minWidth={420}>
                    <Table withTableBorder>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>Ano</Table.Th>
                          <Table.Th ta="right">Valor inicial</Table.Th>
                          <Table.Th ta="right">Depreciação</Table.Th>
                          <Table.Th ta="right">Valor final</Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {eq.linhas.map((l) => {
                          const futuro = l.ano > anoAtual;
                          return (
                            <Table.Tr
                              key={l.ano}
                              bg={futuro ? "var(--mantine-color-petroleo-0)" : undefined}
                            >
                              <Table.Td>
                                {l.ano}
                                {futuro ? " (prev.)" : ""}
                              </Table.Td>
                              <Table.Td ta="right">{eur(l.valor_inicial)}</Table.Td>
                              <Table.Td ta="right">{eur(l.depreciacao)}</Table.Td>
                              <Table.Td ta="right">{eur(l.valor_final)}</Table.Td>
                            </Table.Tr>
                          );
                        })}
                      </Table.Tbody>
                    </Table>
                  </Table.ScrollContainer>
                </div>
              ))}
            </Stack>
          </Collapse>
        </Paper>
      )}
    </Stack>
  );
}
