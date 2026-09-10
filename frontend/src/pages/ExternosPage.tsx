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
  createExterno,
  deleteExterno,
  listExternos,
  updateExterno,
  type Externo,
} from "../api/apoio";
import { extractError } from "../utils/errors";
import { eur } from "../utils/format";
import { ordenarLista, SortableTh, type SortDir } from "../components/SortableTh";

export function ExternosPage() {
  const qc = useQueryClient();
  const [opened, setOpened] = useState(false);
  const [editing, setEditing] = useState<Externo | null>(null);
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
    queryKey: ["externos"],
    queryFn: listExternos,
  });

  const dataOrdenada = ordenarLista(data, sortBy, sortDir, (item, c) => {
    if (c === "total_ganho") return Number(item.total_ganho ?? 0);
    if (c === "num_trabalhos") return item.num_trabalhos ?? 0;
    return (item as unknown as Record<string, unknown>)[c];
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ["externos"] });

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editing) return updateExterno(editing.id, { nome });
      return createExterno({ nome });
    },
    onSuccess: () => {
      invalidate();
      setOpened(false);
      notifications.show({ message: "Externo guardado.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteExterno,
    onSuccess: () => {
      invalidate();
      notifications.show({ message: "Externo removido.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  function openCreate() {
    setEditing(null);
    setNome("");
    setOpened(true);
  }

  function openEdit(item: Externo) {
    setEditing(item);
    setNome(item.nome);
    setOpened(true);
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Externos</Title>
        <Button leftSection={<IconPlus size={16} />} onClick={openCreate}>
          Novo
        </Button>
      </Group>

      <Table.ScrollContainer minWidth={480}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <SortableTh label="Nome" campo="nome" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <SortableTh label="Nº trabalhos" campo="num_trabalhos" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} ta="right" />
              <SortableTh label="Total ganho" campo="total_ganho" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} ta="right" />
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {dataOrdenada.map((item) => (
              <Table.Tr key={item.id}>
                <Table.Td>{item.nome}</Table.Td>
                <Table.Td ta="right">{item.num_trabalhos ?? 0}</Table.Td>
                <Table.Td ta="right">{eur(item.total_ganho)}</Table.Td>
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
                <Table.Td colSpan={4} style={{ textAlign: "center" }}>
                  Sem externos.
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Modal
        opened={opened}
        onClose={() => setOpened(false)}
        title={editing ? "Editar externo" : "Novo externo"}
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
