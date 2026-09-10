import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ActionIcon,
  Button,
  Group,
  Modal,
  NumberInput,
  Stack,
  Table,
  TextInput,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconPencil, IconPlus, IconTrash } from "@tabler/icons-react";

import {
  createEspecialidade,
  deleteEspecialidade,
  listEspecialidades,
  updateEspecialidade,
  type Especialidade,
} from "../api/apoio";
import { extractError } from "../utils/errors";
import { ordenarLista, SortableTh, type SortDir } from "../components/SortableTh";

interface FormState {
  codigo: string;
  descricao: string;
  prazo_top: number | string;
  prazo_ok: number | string;
}

const emptyForm: FormState = { codigo: "", descricao: "", prazo_top: 0, prazo_ok: 0 };

export function EspecialidadesPage() {
  const qc = useQueryClient();
  const [opened, setOpened] = useState(false);
  const [editing, setEditing] = useState<Especialidade | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);

  const [sortBy, setSortBy] = useState<string | null>("codigo");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  function handleSort(campo: string) {
    if (sortBy === campo) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortBy(campo);
      setSortDir("asc");
    }
  }

  const { data = [], isLoading } = useQuery({
    queryKey: ["especialidades"],
    queryFn: listEspecialidades,
  });

  const dataOrdenada = ordenarLista(data, sortBy, sortDir);

  const invalidate = () => qc.invalidateQueries({ queryKey: ["especialidades"] });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        codigo: form.codigo,
        descricao: form.descricao || null,
        prazo_top: Number(form.prazo_top),
        prazo_ok: Number(form.prazo_ok),
      };
      if (editing) return updateEspecialidade(editing.id, payload);
      return createEspecialidade(payload);
    },
    onSuccess: () => {
      invalidate();
      setOpened(false);
      notifications.show({ message: "Especialidade guardada.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEspecialidade,
    onSuccess: () => {
      invalidate();
      notifications.show({ message: "Especialidade removida.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  function openCreate() {
    setEditing(null);
    setForm(emptyForm);
    setOpened(true);
  }

  function openEdit(item: Especialidade) {
    setEditing(item);
    setForm({
      codigo: item.codigo,
      descricao: item.descricao ?? "",
      prazo_top: item.prazo_top,
      prazo_ok: item.prazo_ok,
    });
    setOpened(true);
  }

  return (
    <Stack>
      <Group justify="space-between">
        <Title order={2}>Especialidades</Title>
        <Button leftSection={<IconPlus size={16} />} onClick={openCreate}>
          Nova
        </Button>
      </Group>

      <Table.ScrollContainer minWidth={500}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <SortableTh label="Código" campo="codigo" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <SortableTh label="Descrição" campo="descricao" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <SortableTh label="Prazo TOP (dias)" campo="prazo_top" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <SortableTh label="Prazo OK (dias)" campo="prazo_ok" sortBy={sortBy} sortDir={sortDir} onSort={handleSort} />
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {dataOrdenada.map((item) => (
              <Table.Tr key={item.id}>
                <Table.Td>{item.codigo}</Table.Td>
                <Table.Td>{item.descricao}</Table.Td>
                <Table.Td>{item.prazo_top}</Table.Td>
                <Table.Td>{item.prazo_ok}</Table.Td>
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
                <Table.Td colSpan={5} style={{ textAlign: "center" }}>
                  Sem especialidades.
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Modal
        opened={opened}
        onClose={() => setOpened(false)}
        title={editing ? "Editar especialidade" : "Nova especialidade"}
      >
        <Stack>
          <TextInput
            label="Código"
            required
            value={form.codigo}
            onChange={(e) => setForm({ ...form, codigo: e.currentTarget.value })}
          />
          <TextInput
            label="Descrição"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.currentTarget.value })}
          />
          <NumberInput
            label="Prazo TOP (dias)"
            min={0}
            value={form.prazo_top}
            onChange={(v) => setForm({ ...form, prazo_top: v })}
          />
          <NumberInput
            label="Prazo OK (dias)"
            min={0}
            value={form.prazo_ok}
            onChange={(v) => setForm({ ...form, prazo_ok: v })}
          />
          <Button onClick={() => saveMutation.mutate()} loading={saveMutation.isPending}>
            Guardar
          </Button>
        </Stack>
      </Modal>
    </Stack>
  );
}
