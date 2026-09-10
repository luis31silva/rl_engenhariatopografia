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
  createEquipamento,
  deleteEquipamento,
  listEquipamentos,
  updateEquipamento,
  type Equipamento,
} from "../api/dashboard";
import { extractError } from "../utils/errors";
import { eur } from "../utils/format";

interface FormState {
  nome: string;
  percentagem: number | string; // em percentagem (ex.: 16.66)
  ano_aquisicao: number | string;
  valor: number | string;
}

export function GestaoEquipamentos() {
  const qc = useQueryClient();
  const [opened, setOpened] = useState(false);
  const [editing, setEditing] = useState<Equipamento | null>(null);
  const [form, setForm] = useState<FormState>({
    nome: "",
    percentagem: "",
    ano_aquisicao: new Date().getFullYear(),
    valor: "",
  });

  const { data = [] } = useQuery({ queryKey: ["equipamentos"], queryFn: listEquipamentos });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["equipamentos"] });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        nome: form.nome,
        // Converte de percentagem (16.66) para fração (0.1666).
        percentagem: form.percentagem === "" ? 0 : Number(form.percentagem) / 100,
        ano_aquisicao: Number(form.ano_aquisicao),
        valor: form.valor === "" ? 0 : Number(form.valor),
      };
      if (editing) return updateEquipamento(editing.id, payload);
      return createEquipamento(payload);
    },
    onSuccess: () => {
      invalidate();
      setOpened(false);
      notifications.show({ message: "Equipamento guardado.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEquipamento,
    onSuccess: () => {
      invalidate();
      notifications.show({ message: "Equipamento removido.", color: "green" });
    },
    onError: (e) => notifications.show({ message: extractError(e), color: "red" }),
  });

  function openCreate() {
    setEditing(null);
    setForm({ nome: "", percentagem: "", ano_aquisicao: new Date().getFullYear(), valor: "" });
    setOpened(true);
  }
  function openEdit(item: Equipamento) {
    setEditing(item);
    setForm({
      nome: item.nome,
      percentagem: Number(item.percentagem) * 100,
      ano_aquisicao: item.ano_aquisicao,
      valor: Number(item.valor),
    });
    setOpened(true);
  }

  return (
    <Paper withBorder radius="md" p="md">
      <Group justify="space-between" mb="sm">
        <Title order={4}>Equipamentos</Title>
        <Button size="xs" leftSection={<IconPlus size={14} />} onClick={openCreate}>
          Adicionar equipamento
        </Button>
      </Group>

      <Table.ScrollContainer minWidth={520}>
        <Table striped>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Nome</Table.Th>
              <Table.Th ta="right">% anual</Table.Th>
              <Table.Th ta="right">Ano aquisição</Table.Th>
              <Table.Th ta="right">Valor aquisição</Table.Th>
              <Table.Th />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {data.map((eq) => (
              <Table.Tr key={eq.id}>
                <Table.Td>{eq.nome}</Table.Td>
                <Table.Td ta="right">{(Number(eq.percentagem) * 100).toFixed(2)}%</Table.Td>
                <Table.Td ta="right">{eq.ano_aquisicao}</Table.Td>
                <Table.Td ta="right">{eur(eq.valor)}</Table.Td>
                <Table.Td>
                  <Group gap="xs" justify="flex-end">
                    <ActionIcon variant="subtle" onClick={() => openEdit(eq)}>
                      <IconPencil size={16} />
                    </ActionIcon>
                    <ActionIcon variant="subtle" color="red" onClick={() => deleteMutation.mutate(eq.id)}>
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {data.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={5}>
                  <Text ta="center" c="dimmed" size="sm">
                    Sem equipamentos registados.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Table.ScrollContainer>

      <Modal
        opened={opened}
        onClose={() => setOpened(false)}
        title={editing ? "Editar equipamento" : "Novo equipamento"}
      >
        <Stack>
          <TextInput
            label="Nome"
            required
            placeholder="ex.: Estação Total Leica"
            value={form.nome}
            onChange={(e) => setForm({ ...form, nome: e.currentTarget.value })}
          />
          <NumberInput
            label="Depreciação anual (%)"
            min={0}
            max={100}
            decimalScale={2}
            suffix="%"
            value={form.percentagem}
            onChange={(v) => setForm({ ...form, percentagem: v })}
          />
          <NumberInput
            label="Ano de aquisição"
            min={1900}
            max={2200}
            value={form.ano_aquisicao}
            onChange={(v) => setForm({ ...form, ano_aquisicao: v })}
          />
          <NumberInput
            label="Valor de aquisição (€)"
            min={0}
            decimalScale={2}
            value={form.valor}
            onChange={(v) => setForm({ ...form, valor: v })}
          />
          <Button onClick={() => saveMutation.mutate()} loading={saveMutation.isPending}>
            Guardar
          </Button>
        </Stack>
      </Modal>
    </Paper>
  );
}
