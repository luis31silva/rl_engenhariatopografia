import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Card,
  Grid,
  Group,
  Loader,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
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

import { getDashboard, getEspecialidadesResumo } from "../api/dashboard";
import { eur, nomeMes, nomeMesCurto } from "../utils/format";

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
  const { data: espResumo = [] } = useQuery({
    queryKey: ["especialidades-resumo"],
    queryFn: getEspecialidadesResumo,
  });

  // Anos com dados mensais, para o seletor do resumo por mês.
  const anosMensais = useMemo(() => {
    const set = new Set<number>();
    data?.resumo_mensal.forEach((r) => set.add(r.ano));
    return Array.from(set).sort((a, b) => b - a);
  }, [data]);

  const [anoMes, setAnoMes] = useState<number | null>(null);
  const anoMesSel = anoMes ?? anosMensais[0] ?? null;

  // Anos com dados por especialidade.
  const anosEsp = useMemo(() => {
    const set = new Set<number>();
    espResumo.forEach((e) => e.resumo_mensal.forEach((r) => set.add(r.ano)));
    return Array.from(set).sort((a, b) => b - a);
  }, [espResumo]);

  const [anoEsp, setAnoEsp] = useState<number | null>(null);
  const anoEspSel = anoEsp ?? anosEsp[0] ?? null;

  if (isLoading) {
    return (
      <Group justify="center" mt="xl">
        <Loader />
      </Group>
    );
  }
  if (!data) return null;

  const chartData = data.resumo_anual.map((r) => ({
    ano: String(r.ano),
    Brutos: Number(r.brutos),
    Custos: Number(r.custos),
    Líquidos: Number(r.liquidos),
  }));

  const mensalDoAno = data.resumo_mensal.filter((r) => r.ano === anoMesSel);
  const chartMensal = mensalDoAno.map((r) => ({
    mes: nomeMesCurto(r.mes),
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

      {/* ---- Resumo por mês ---- */}
      <Paper withBorder radius="md" p="md">
        <Group justify="space-between" mb="sm">
          <Title order={4}>Resumo por mês</Title>
          <Select
            aria-label="Ano do resumo por mês"
            data={anosMensais.map((a) => String(a))}
            value={anoMesSel != null ? String(anoMesSel) : null}
            onChange={(v) => setAnoMes(v ? Number(v) : null)}
            allowDeselect={false}
            w={110}
            disabled={anosMensais.length === 0}
          />
        </Group>
        {chartMensal.length > 0 && (
          <div style={{ width: "100%", height: 320, marginBottom: "var(--mantine-spacing-md)" }}>
            <ResponsiveContainer>
              <BarChart data={chartMensal}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" />
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
        )}
        <Table.ScrollContainer minWidth={480}>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Mês</Table.Th>
                <Table.Th ta="right">Brutos</Table.Th>
                <Table.Th ta="right">Custos</Table.Th>
                <Table.Th ta="right">Líquidos</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {mensalDoAno.map((r) => (
                <Table.Tr key={r.mes}>
                  <Table.Td>{nomeMes(r.mes)}</Table.Td>
                  <Table.Td ta="right">{eur(r.brutos)}</Table.Td>
                  <Table.Td ta="right">{eur(r.custos)}</Table.Td>
                  <Table.Td ta="right">{eur(r.liquidos)}</Table.Td>
                </Table.Tr>
              ))}
              {mensalDoAno.length === 0 && (
                <Table.Tr>
                  <Table.Td colSpan={4}>
                    <Text ta="center" c="dimmed">
                      Sem dados mensais para {anoMesSel ?? "este ano"}.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              )}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>

      {/* ---- Resumo por especialidade (mês a mês) ---- */}
      <Paper withBorder radius="md" p="md">
        <Group justify="space-between" mb="sm">
          <Title order={4}>Especialidades por mês</Title>
          <Select
            aria-label="Ano do resumo por especialidade"
            data={anosEsp.map((a) => String(a))}
            value={anoEspSel != null ? String(anoEspSel) : null}
            onChange={(v) => setAnoEsp(v ? Number(v) : null)}
            allowDeselect={false}
            w={110}
            disabled={anosEsp.length === 0}
          />
        </Group>
        <Table.ScrollContainer minWidth={560}>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Especialidade</Table.Th>
                <Table.Th>Mês</Table.Th>
                <Table.Th ta="right">Nº trabalhos</Table.Th>
                <Table.Th ta="right">Valor</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {espResumo.flatMap((esp) =>
                esp.resumo_mensal
                  .filter((r) => r.ano === anoEspSel)
                  .map((r) => (
                    <Table.Tr key={`${esp.especialidade_id}-${r.mes}`}>
                      <Table.Td>{esp.codigo}</Table.Td>
                      <Table.Td>{nomeMes(r.mes)}</Table.Td>
                      <Table.Td ta="right">{r.num_itens}</Table.Td>
                      <Table.Td ta="right">{eur(r.valor)}</Table.Td>
                    </Table.Tr>
                  )),
              )}
              {espResumo.every(
                (esp) => esp.resumo_mensal.filter((r) => r.ano === anoEspSel).length === 0,
              ) && (
                <Table.Tr>
                  <Table.Td colSpan={4}>
                    <Text ta="center" c="dimmed">
                      Sem dados por especialidade para {anoEspSel ?? "este ano"}.
                    </Text>
                  </Table.Td>
                </Table.Tr>
              )}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>
    </Stack>
  );
}
