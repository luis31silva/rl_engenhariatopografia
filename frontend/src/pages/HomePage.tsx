import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ActionIcon,
  Box,
  Button,
  Collapse,
  Group,
  Menu,
  Pagination,
  Paper,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  UnstyledButton,
} from "@mantine/core";
import { useDebouncedValue } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import {
  IconChevronDown,
  IconChevronRight,
  IconFileText,
  IconPencil,
  IconPlus,
  IconSearch,
  IconTrash,
} from "@tabler/icons-react";

import { listEspecialidades, listExternos, listIntermediarios } from "../api/apoio";
import {
  createTrabalho,
  deleteTrabalho,
  downloadFatura,
  listTrabalhos,
  SITUACOES,
  updateTrabalho,
  type Estado,
  type Situacao,
  type Trabalho,
  type TrabalhoInput,
} from "../api/trabalhos";
import { AlertasPanel } from "../components/AlertasPanel";
import { EstadoBadge } from "../components/EstadoBadge";
import { SituacaoBadge } from "../components/SituacaoBadge";
import { SortableTh } from "../components/SortableTh";
import { TrabalhoForm } from "../components/TrabalhoForm";
import { extractError } from "../utils/errors";
import { eur } from "../utils/format";

const PAGE_SIZE = 25;
const ESTADOS: Estado[] = ["TOP", "OK", "MAU", "PENDENTE"];

function LinhaTrabalho({
  t,
  onEdit,
  onDelete,
  onFatura,
  onSituacaoTodos,
}: {
  t: Trabalho;
  onEdit: (t: Trabalho) => void;
  onDelete: (id: number) => void;
  onFatura: (t: Trabalho) => void;
  onSituacaoTodos: (id: number, situacao: Situacao) => void;
}) {
  const [aberto, setAberto] = useState(false);
  const especialidades = t.itens.map((i) => i.especialidade_codigo).filter(Boolean);
  const resumoEspec =
    especialidades.length === 0
      ? "—"
      : especialidades.length <= 2
        ? especialidades.join(", ")
        : `${especialidades.slice(0, 2).join(", ")} +${especialidades.length - 2}`;

  return (
    <>
      <Table.Tr style={{ cursor: t.itens.length ? "pointer" : "default" }}>
        <Table.Td onClick={() => t.itens.length && setAberto((v) => !v)}>
          {t.itens.length > 0 &&
            (aberto ? <IconChevronDown size={16} /> : <IconChevronRight size={16} />)}
        </Table.Td>
        <Table.Td onClick={() => t.itens.length && setAberto((v) => !v)}>{t.referencia}</Table.Td>
        <Table.Td onClick={() => t.itens.length && setAberto((v) => !v)}>{t.cliente}</Table.Td>
        <Table.Td>{resumoEspec}</Table.Td>
        <Table.Td>{t.intermediario_nome}</Table.Td>
        <Table.Td ta="right">{eur(t.valor_total)}</Table.Td>
        <Table.Td>
          {/* Menu para mudar a situação (aplica a todas as especialidades). */}
          <Menu position="bottom-start" withinPortal>
            <Menu.Target>
              <UnstyledButton title="Alterar situação">
                <Group gap={4} wrap="nowrap">
                  <SituacaoBadge situacao={t.situacao_trabalho} />
                  <IconChevronDown size={14} style={{ opacity: 0.5 }} />
                </Group>
              </UnstyledButton>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Label>Marcar como</Menu.Label>
              {SITUACOES.map((s) => (
                <Menu.Item
                  key={s}
                  onClick={() => onSituacaoTodos(t.id, s)}
                  leftSection={<SituacaoBadge situacao={s} />}
                />
              ))}
            </Menu.Dropdown>
          </Menu>
        </Table.Td>
        <Table.Td>
          <Group gap="xs" justify="flex-end" wrap="nowrap">
            <ActionIcon variant="subtle" title="Gerar recibo (PDF)" onClick={() => onFatura(t)}>
              <IconFileText size={16} />
            </ActionIcon>
            <ActionIcon variant="subtle" title="Editar" onClick={() => onEdit(t)}>
              <IconPencil size={16} />
            </ActionIcon>
            <ActionIcon variant="subtle" color="red" title="Apagar" onClick={() => onDelete(t.id)}>
              <IconTrash size={16} />
            </ActionIcon>
          </Group>
        </Table.Td>
      </Table.Tr>
      <Table.Tr>
        <Table.Td colSpan={8} p={0} style={{ border: aberto ? undefined : "none" }}>
          <Collapse in={aberto}>
            <Box p="sm" bg="var(--mantine-color-gray-0)">
              <Table>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Especialidade</Table.Th>
                    <Table.Th>Adjudicação</Table.Th>
                    <Table.Th>Entrega</Table.Th>
                    <Table.Th>Externo</Table.Th>
                    <Table.Th ta="right">Valor</Table.Th>
                    <Table.Th ta="right">Valor externo</Table.Th>
                    <Table.Th>Estado</Table.Th>
                    <Table.Th>Situação</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {t.itens.map((i) => (
                    <Table.Tr key={i.id}>
                      <Table.Td>{i.especialidade_codigo ?? "—"}</Table.Td>
                      <Table.Td>{i.data_adjudicacao ?? "—"}</Table.Td>
                      <Table.Td>{i.data_entrega ?? "—"}</Table.Td>
                      <Table.Td>{i.externo_nome ?? "—"}</Table.Td>
                      <Table.Td ta="right">{eur(i.valor)}</Table.Td>
                      <Table.Td ta="right">{eur(i.valor_externo)}</Table.Td>
                      <Table.Td>
                        <EstadoBadge estado={i.estado} />
                      </Table.Td>
                      <Table.Td>
                        <SituacaoBadge situacao={i.situacao} />
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            </Box>
          </Collapse>
        </Table.Td>
      </Table.Tr>
    </>
  );
}

export function HomePage() {
  const qc = useQueryClient();
  const [opened, setOpened] = useState(false);
  const [editing, setEditing] = useState<Trabalho | null>(null);

  const [busca, setBusca] = useState("");
  const [buscaDebounced] = useDebouncedValue(busca, 300);
  const [especialidadeId, setEspecialidadeId] = useState<string | null>(null);
  const [intermediarioId, setIntermediarioId] = useState<string | null>(null);
  const [externoId, setExternoId] = useState<string | null>(null);
  const [ano, setAno] = useState<string | null>(null);
  const [estado, setEstado] = useState<string | null>(null);
  const [situacao, setSituacao] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<string>("id");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  function handleSort(campo: string) {
    if (sortBy === campo) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(campo);
      setSortDir("asc");
    }
    setPage(1);
  }

  const { data: especialidades = [] } = useQuery({ queryKey: ["especialidades"], queryFn: listEspecialidades });
  const { data: intermediarios = [] } = useQuery({ queryKey: ["intermediarios"], queryFn: listIntermediarios });
  const { data: externos = [] } = useQuery({ queryKey: ["externos"], queryFn: listExternos });

  const filtros = {
    q: buscaDebounced,
    especialidade_id: especialidadeId ? Number(especialidadeId) : null,
    intermediario_id: intermediarioId ? Number(intermediarioId) : null,
    externo_id: externoId ? Number(externoId) : null,
    ano: ano ? Number(ano) : null,
    estado: (estado as Estado) ?? null,
    situacao: (situacao as Situacao) ?? null,
    order_by: sortBy,
    order_dir: sortDir,
    page,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading } = useQuery({
    queryKey: ["trabalhos", filtros],
    queryFn: () => listTrabalhos(filtros),
  });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["trabalhos"] });
    qc.invalidateQueries({ queryKey: ["alertas"] });
  };

  const saveMutation = useMutation({
    mutationFn: (input: TrabalhoInput) =>
      editing ? updateTrabalho(editing.id, input) : createTrabalho(input),
    onSuccess: () => {
      invalidate();
      setOpened(false);
      notifications.show({ message: "Trabalho guardado.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteTrabalho,
    onSuccess: () => {
      invalidate();
      notifications.show({ message: "Trabalho removido.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  const situacaoTodosMutation = useMutation({
    mutationFn: ({ id, situacao }: { id: number; situacao: Situacao }) =>
      updateTrabalho(id, { situacao_todos: situacao }),
    onSuccess: () => {
      invalidate();
      notifications.show({ message: "Situação atualizada.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  function openCreate() {
    setEditing(null);
    setOpened(true);
  }
  function openEdit(t: Trabalho) {
    setEditing(t);
    setOpened(true);
  }
  async function handleFatura(t: Trabalho) {
    try {
      await downloadFatura(t.id, t.referencia);
    } catch (e) {
      notifications.show({ message: extractError(e), color: "red" });
    }
  }
  function resetPage<T>(setter: (v: T) => void) {
    return (v: T) => {
      setter(v);
      setPage(1);
    };
  }

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const items = data?.items ?? [];

  const anoAtual = new Date().getFullYear();
  const anos = Array.from({ length: anoAtual - 2015 + 1 }, (_, i) => String(anoAtual - i));

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Trabalhos</Title>
        <Button leftSection={<IconPlus size={16} />} onClick={openCreate}>
          Novo trabalho
        </Button>
      </Group>

      <AlertasPanel />

      <Paper withBorder p="md" radius="md">
        <Group align="flex-end" gap="sm" wrap="wrap">
          <TextInput
            label="Pesquisar"
            placeholder="Cliente, ref., localidade…"
            leftSection={<IconSearch size={16} />}
            value={busca}
            onChange={(e) => {
              setBusca(e.currentTarget.value);
              setPage(1);
            }}
            style={{ flex: "1 1 220px" }}
          />
          <Select
            label="Especialidade"
            placeholder="Todas"
            clearable
            searchable
            data={especialidades.map((e) => ({ value: String(e.id), label: e.codigo }))}
            value={especialidadeId}
            onChange={resetPage(setEspecialidadeId)}
            w={150}
          />
          <Select
            label="Intermediário"
            placeholder="Todos"
            clearable
            searchable
            data={intermediarios.map((i) => ({ value: String(i.id), label: i.nome }))}
            value={intermediarioId}
            onChange={resetPage(setIntermediarioId)}
            w={170}
          />
          <Select
            label="Externo"
            placeholder="Todos"
            clearable
            searchable
            data={externos.map((x) => ({ value: String(x.id), label: x.nome }))}
            value={externoId}
            onChange={resetPage(setExternoId)}
            w={150}
          />
          <Select label="Ano" placeholder="Todos" clearable data={anos} value={ano} onChange={resetPage(setAno)} w={110} />
          <Select
            label="Estado"
            placeholder="Todos"
            clearable
            data={ESTADOS}
            value={estado}
            onChange={resetPage(setEstado)}
            w={130}
          />
          <Select
            label="Situação"
            placeholder="Todas"
            clearable
            data={SITUACOES}
            value={situacao}
            onChange={resetPage(setSituacao)}
            w={160}
          />
        </Group>
      </Paper>

      <Table.ScrollContainer minWidth={960}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th w={30} />
              <SortableTh label="Ref." campo="referencia" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <SortableTh label="Cliente" campo="cliente" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <Table.Th>Especialidades</Table.Th>
              <Table.Th>Intermediário</Table.Th>
              <Table.Th ta="right">Valor total</Table.Th>
              <Table.Th>Situação</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {items.map((t) => (
              <LinhaTrabalho
                key={t.id}
                t={t}
                onEdit={openEdit}
                onDelete={(id) => deleteMutation.mutate(id)}
                onFatura={handleFatura}
                onSituacaoTodos={(id, sit) => situacaoTodosMutation.mutate({ id, situacao: sit })}
              />
            ))}
            {!isLoading && items.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={8}>
                  <Text ta="center" c="dimmed">
                    Sem resultados para os filtros aplicados.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Group justify="space-between">
        <Text size="sm" c="dimmed">
          {total} trabalho(s)
        </Text>
        <Pagination value={page} onChange={setPage} total={totalPages} />
      </Group>

      <TrabalhoForm
        opened={opened}
        onClose={() => setOpened(false)}
        onSubmit={(input) => saveMutation.mutate(input)}
        submitting={saveMutation.isPending}
        initial={editing}
      />
    </Stack>
  );
}
