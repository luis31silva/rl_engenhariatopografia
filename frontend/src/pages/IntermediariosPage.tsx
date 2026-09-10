import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ActionIcon,
  Button,
  Group,
  Modal,
  Stack,
  Table,
  TextInput,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconPencil, IconPlus, IconTrash } from "@tabler/icons-react";

import {
  createIntermediario,
  deleteIntermediario,
  listIntermediarios,
  updateIntermediario,
  type Intermediario,
} from "../api/apoio";
import { extractError } from "../utils/errors";
import { eur } from "../utils/format";
import { ordenarLista, SortableTh, type SortDir } from "../components/SortableTh";

export function IntermediariosPage() {
  const qc = useQueryClient();
  const [opened, setOpened] = useState(false);
  const [editing, setEditing] = useState<Intermediario | null>(null);
  const [nome, setNome] = useState("");

  const [sortBy, setSortBy] = useState<string | null>("nome");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  function handleSort(campo: string) {
    if (sortBy === campo) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortBy(campo);
      setSortDir("asc");
    }
  }

  const { data = [], isLoading } = useQuery({
    queryKey: ["intermediarios"],
    queryFn: listIntermediarios,
  });

  const anoAtual = new Date().getFullYear();

  const dataOrdenada = ordenarLista(data, sortBy, sortDir, (item, c) => {
    if (c === "num_trabalhos") return item.num_trabalhos ?? 0;
    if (c === "valor_total") return Number(item.valor_total ?? 0);
    if (c === "valor_medio") return Number(item.valor_medio ?? 0);
    if (c === "num_trabalhos_ano") return item.num_trabalhos_ano ?? 0;
    if (c === "valor_ano") return Number(item.valor_ano ?? 0);
    return (item as unknown as Record<string, unknown>)[c];
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["intermediarios"] });

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editing) return updateIntermediario(editing.id, { nome });
      return createIntermediario({ nome });
    },
    onSuccess: () => {
      invalidate();
      setOpened(false);
      notifications.show({ message: "Intermediário guardado.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteIntermediario,
    onSuccess: () => {
      invalidate();
      notifications.show({ message: "Intermediário removido.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  function openCreate() {
    setEditing(null);
    setNome("");
    setOpened(true);
  }

  function openEdit(item: Intermediario) {
    setEditing(item);
    setNome(item.nome);
    setOpened(true);
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Intermediários</Title>
        <Button leftSection={<IconPlus size={16} />} onClick={openCreate}>
          Novo
        </Button>
      </Group>

      <Table.ScrollContainer minWidth={760}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <SortableTh label="Nome" campo="nome" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <SortableTh label="Nº trabalhos" campo="num_trabalhos" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} ta="right" />
              <SortableTh label="Valor total" campo="valor_total" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} ta="right" />
              <SortableTh label="Valor médio" campo="valor_medio" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} ta="right" />
              <SortableTh label={`Nº trab. ${anoAtual}`} campo="num_trabalhos_ano" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} ta="right" />
              <SortableTh label={`Valor ${anoAtual}`} campo="valor_ano" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} ta="right" />
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {dataOrdenada.map((item) => (
              <Table.Tr key={item.id}>
                <Table.Td>{item.nome}</Table.Td>
                <Table.Td ta="right">{item.num_trabalhos ?? 0}</Table.Td>
                <Table.Td ta="right">{eur(item.valor_total)}</Table.Td>
                <Table.Td ta="right">{eur(item.valor_medio)}</Table.Td>
                <Table.Td ta="right">{item.num_trabalhos_ano ?? 0}</Table.Td>
                <Table.Td ta="right">{eur(item.valor_ano)}</Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <ActionIcon variant="subtle" onClick={() => openEdit(item)}>
                      <IconPencil size={16} />
                    </ActionIcon>
                    <ActionIcon
                      variant="subtle"
                      color="red"
                      onClick={() => deleteMutation.mutate(item.id)}
                    >
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {!isLoading && data.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7} style={{ textAlign: "center" }}>
                  Sem intermediários.
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Modal
        opened={opened}
        onClose={() => setOpened(false)}
        title={editing ? "Editar intermediário" : "Novo intermediário"}
      >
        <Stack>
          <TextInput
            label="Nome"
            required
            value={nome}
            onChange={(e) => setNome(e.currentTarget.value)}
          />
          <Button onClick={() => saveMutation.mutate()} loading={saveMutation.isPending}>
            Guardar
          </Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
