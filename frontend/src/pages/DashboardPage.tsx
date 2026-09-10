import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  Collapse,
  Grid,
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
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getDashboard } from "../api/dashboard";
import { GestaoCustos } from "../components/GestaoCustos";
import { GestaoEquipamentos } from "../components/GestaoEquipamentos";
import { eur } from "../utils/format";

function pct(v: number | null): string {
  return v == null ? "—" : `${v.toFixed(1)}%`;
}

function TotalCard({ label, valor, cor }: { label: string; valor: string; cor?: string }) {
  return (
    <Card withBorder radius="md" padding="lg">
      <Text size="sm" c="dimmed">
        {label}
      </Text>
      <Text size="xl" fw={700} c={cor}>
        {valor}
      </Text>
    </Card>
  );
}

export function DashboardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: getDashboard });
  const [depreciacaoAberta, setDepreciacaoAberta] = useState(false);

  if (isLoading) {
    return (
      <Group justify="center" mt="xl">
        <Loader />
      </Group>
    );
  }
  if (!data) return null;

  const anoAtual = new Date().getFullYear();

  const chartData = data.resumo_anual.map((r) => ({
    ano: String(r.ano),
    Brutos: Number(r.brutos),
    Custos: Number(r.custos),
    Líquidos: Number(r.liquidos),
  }));

  return (
    <Stack>
      <Title order={2}>Relatório de Contas</Title>

      <Grid>
        <Grid.Col span={{ base: 12, sm: 4 }}>
          <TotalCard label="Total brutos" valor={eur(data.total_brutos)} />
        </Grid.Col>
        <Grid.Col span={{ base: 12, sm: 4 }}>
          <TotalCard label="Total custos" valor={eur(data.total_custos)} cor="red" />
        </Grid.Col>
        <Grid.Col span={{ base: 12, sm: 4 }}>
          <TotalCard label="Total líquidos" valor={eur(data.total_liquidos)} cor="green" />
        </Grid.Col>
      </Grid>

      <Paper withBorder radius="md" p="md">
        <Title order={4} mb="sm">
          Evolução anual
        </Title>
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="ano" />
              <YAxis />
              <Tooltip
                formatter={(v: number) => eur(v)}
                cursor={{ fill: "rgba(0,0,0,0.06)" }}
                contentStyle={{
                  backgroundColor: "#111417",
                  border: "none",
                  borderRadius: 8,
                  color: "#fff",
                }}
                labelStyle={{ color: "#fff", fontWeight: 600 }}
                itemStyle={{ color: "#fff" }}
              />
              <Legend />
              <Bar dataKey="Brutos" fill="#297f6d" />
              <Bar dataKey="Custos" fill="#e8590c" />
              <Bar dataKey="Líquidos" fill="#82ab51" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Paper>

      <Paper withBorder radius="md" p="md">
        <Title order={4} mb="sm">
          Resumo por ano
        </Title>
        <Table.ScrollContainer minWidth={560}>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Ano</Table.Th>
                <Table.Th ta="right">Brutos</Table.Th>
                <Table.Th ta="right">Custos</Table.Th>
                <Table.Th ta="right">Líquidos</Table.Th>
                <Table.Th ta="right">% Liquidez</Table.Th>
                <Table.Th ta="right">Variação</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {data.resumo_anual.map((r) => (
                <Table.Tr key={r.ano}>
                  <Table.Td>{r.ano}</Table.Td>
                  <Table.Td ta="right">{eur(r.brutos)}</Table.Td>
                  <Table.Td ta="right">{eur(r.custos)}</Table.Td>
                  <Table.Td ta="right">{eur(r.liquidos)}</Table.Td>
                  <Table.Td ta="right">{pct(r.liquidez_pct)}</Table.Td>
                  <Table.Td ta="right" c={r.variacao_pct != null && r.variacao_pct < 0 ? "red" : undefined}>
                    {pct(r.variacao_pct)}
                  </Table.Td>
                </Table.Tr>
              ))}
              {data.resumo_anual.length === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={6}>
                    <Text ta="center" c="dimmed">
                      Sem dados. Adicione trabalhos com datas de adjudicação.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              )}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>

      <GestaoEquipamentos />
      <GestaoCustos />

      {data.depreciacao.length > 0 && (
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
