import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ActionIcon,
  Button,
  Group,
  Modal,
  NumberInput,
  Paper,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconPencil, IconPlus, IconTrash } from "@tabler/icons-react";

import {
  createCusto,
  deleteCusto,
  listCustos,
  updateCusto,
  type CustoAnual,
} from "../api/dashboard";
import { extractError } from "../utils/errors";
import { eur } from "../utils/format";

interface FormState {
  ano: number | string;
  valor: number | string;
  descricao: string;
}

export function GestaoCustos() {
  const qc = useQueryClient();
  const [opened, setOpened] = useState(false);
  const [editing, setEditing] = useState<CustoAnual | null>(null);
  const [form, setForm] = useState<FormState>({ ano: new Date().getFullYear(), valor: "", descricao: "" });

  const { data = [] } = useQuery({ queryKey: ["custos"], queryFn: listCustos });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["custos"] });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        ano: Number(form.ano),
        valor: form.valor === "" ? 0 : Number(form.valor),
        descricao: form.descricao || null,
      };
      if (editing) return updateCusto(editing.id, payload);
      return createCusto(payload);
    },
    onSuccess: () => {
      invalidate();
      setOpened(false);
      notifications.show({ message: "Custo guardado.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCusto,
    onSuccess: () => {
      invalidate();
      notifications.show({ message: "Custo removido.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  function openCreate() {
    setEditing(null);
    setForm({ ano: new Date().getFullYear(), valor: "", descricao: "" });
    setOpened(true);
  }
  function openEdit(item: CustoAnual) {
    setEditing(item);
    setForm({ ano: item.ano, valor: Number(item.valor), descricao: item.descricao ?? "" });
    setOpened(true);
  }

  const ordenados = [...data].sort((a, b) => b.ano - a.ano);

  return (
    <Paper withBorder radius="md" p="md">
      <Group justify="space-between" mb="sm">
        <Title order={4}>Custos anuais</Title>
        <Button size="xs" leftSection={<IconPlus size={14} />} onClick={openCreate}>
          Adicionar custo
        </Button>
      </Group>

      <Table.ScrollContainer minWidth={420}>
        <Table striped>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Ano</Table.Th>
              <Table.Th>Descrição</Table.Th>
              <Table.Th ta="right">Valor</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {ordenados.map((c) => (
              <Table.Tr key={c.id}>
                <Table.Td>{c.ano}</Table.Td>
                <Table.Td>{c.descricao || "—"}</Table.Td>
                <Table.Td ta="right">{eur(c.valor)}</Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <ActionIcon variant="subtle" onClick={() => openEdit(c)}>
                      <IconPencil size={16} />
                    </ActionIcon>
                    <ActionIcon variant="subtle" color="red" onClick={() => deleteMutation.mutate(c.id)}>
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {data.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={4}>
                  <Text ta="center" c="dimmed" size="sm">
                    Sem custos anuais registados.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Modal opened={opened} onClose={() => setOpened(false)} title={editing ? "Editar custo" : "Novo custo anual"}>
        <Stack>
          <NumberInput
            label="Ano"
            required
            min={1900}
            max={2200}
            value={form.ano}
            onChange={(v) => setForm({ ...form, ano: v })}
          />
          <NumberInput
            label="Valor (€)"
            min={0}
            decimalScale={2}
            value={form.valor}
            onChange={(v) => setForm({ ...form, valor: v })}
          />
          <TextInput
            label="Descrição"
            placeholder="ex.: Seguros, contabilista, software…"
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.currentTarget.value })}
          />
          <Button onClick={() => saveMutation.mutate()} loading={saveMutation.isPending}>
            Guardar
          </Button>
        </Stack>
      </Modal>
    </Paper>
  );
}
