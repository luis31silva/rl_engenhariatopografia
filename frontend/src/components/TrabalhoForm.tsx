import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ActionIcon,
  Button,
  Divider,
  Grid,
  Group,
  Modal,
  NumberInput,
  Paper,
  Select,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { IconPlus, IconTrash } from "@tabler/icons-react";

import { listEspecialidades, listExternos, listIntermediarios } from "../api/apoio";
import {
  getProximaReferencia,
  SITUACOES,
  type Situacao,
  type Trabalho,
  type TrabalhoInput,
  type TrabalhoItemInput,
} from "../api/trabalhos";

interface Props {
  opened: boolean;
  onClose: () => void;
  onSubmit: (input: TrabalhoInput) => void;
  submitting?: boolean;
  initial?: Trabalho | null;
}

interface ItemState {
  especialidade_id: string | null;
  externo_id: string | null;
  valor: number | string;
  valor_externo: number | string;
  data_adjudicacao: Date | null;
  data_entrega: Date | null;
  situacao: Situacao | null;
  observacoes: string;
}

interface FormState {
  referencia: string;
  cliente: string;
  contacto: string;
  localidade: string;
  endereco: string;
  intermediario_id: string | null;
  itens: ItemState[];
}

const itemVazio: ItemState = {
  especialidade_id: null,
  externo_id: null,
  valor: "",
  valor_externo: "",
  data_adjudicacao: null,
  data_entrega: null,
  situacao: null,
  observacoes: "",
};

const empty: FormState = {
  referencia: "",
  cliente: "",
  contacto: "",
  localidade: "",
  endereco: "",
  intermediario_id: null,
  itens: [{ ...itemVazio }],
};

function toDate(s?: string | null): Date | null {
  return s ? new Date(s) : null;
}
function toISO(d: Date | null): string | null {
  if (!d) return null;
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export function TrabalhoForm({ opened, onClose, onSubmit, submitting, initial }: Props) {
  const [form, setForm] = useState<FormState>(empty);

  const { data: especialidades = [] } = useQuery({ queryKey: ["especialidades"], queryFn: listEspecialidades });
  const { data: intermediarios = [] } = useQuery({ queryKey: ["intermediarios"], queryFn: listIntermediarios });
  const { data: externos = [] } = useQuery({ queryKey: ["externos"], queryFn: listExternos });

  useEffect(() => {
    if (initial) {
      setForm({
        referencia: initial.referencia ?? "",
        cliente: initial.cliente ?? "",
        contacto: initial.contacto ?? "",
        localidade: initial.localidade ?? "",
        endereco: initial.endereco ?? "",
        intermediario_id: initial.intermediario_id ? String(initial.intermediario_id) : null,
        itens:
          initial.itens.length > 0
            ? initial.itens.map((i) => ({
                especialidade_id: i.especialidade_id ? String(i.especialidade_id) : null,
                externo_id: i.externo_id ? String(i.externo_id) : null,
                valor: i.valor != null ? Number(i.valor) : "",
                valor_externo: i.valor_externo != null ? Number(i.valor_externo) : "",
                data_adjudicacao: toDate(i.data_adjudicacao),
                data_entrega: toDate(i.data_entrega),
                situacao: i.situacao ?? null,
                observacoes: i.observacoes ?? "",
              }))
            : [{ ...itemVazio }],
      });
    } else {
      setForm({ ...empty, itens: [{ ...itemVazio }] });
      // Trabalho novo: sugerir a próxima referência (NNN.AA).
      if (opened) {
        getProximaReferencia()
          .then((ref) => setForm((f) => (f.referencia === "" ? { ...f, referencia: ref } : f)))
          .catch(() => {
            /* se falhar, o utilizador preenche manualmente */
          });
      }
    }
  }, [initial, opened]);

  function setItem(idx: number, patch: Partial<ItemState>) {
    setForm((f) => ({
      ...f,
      itens: f.itens.map((it, i) => (i === idx ? { ...it, ...patch } : it)),
    }));
  }
  function addItem() {
    setForm((f) => ({ ...f, itens: [...f.itens, { ...itemVazio }] }));
  }
  function removeItem(idx: number) {
    setForm((f) => ({ ...f, itens: f.itens.filter((_, i) => i !== idx) }));
  }
  function aplicarSituacaoATodas(situacao: Situacao | null) {
    setForm((f) => ({ ...f, itens: f.itens.map((it) => ({ ...it, situacao })) }));
  }

  function handleSubmit() {
    const itens: TrabalhoItemInput[] = form.itens.map((it) => ({
      especialidade_id: it.especialidade_id ? Number(it.especialidade_id) : null,
      externo_id: it.externo_id ? Number(it.externo_id) : null,
      valor: it.valor === "" ? null : Number(it.valor),
      valor_externo: it.valor_externo === "" ? null : Number(it.valor_externo),
      data_adjudicacao: toISO(it.data_adjudicacao),
      data_entrega: toISO(it.data_entrega),
      situacao: it.situacao,
      observacoes: it.observacoes || null,
    }));

    const input: TrabalhoInput = {
      referencia: form.referencia || null,
      cliente: form.cliente || null,
      contacto: form.contacto || null,
      localidade: form.localidade || null,
      endereco: form.endereco || null,
      intermediario_id: form.intermediario_id ? Number(form.intermediario_id) : null,
      itens,
    };
    onSubmit(input);
  }

  const especOptions = especialidades.map((e) => ({ value: String(e.id), label: e.codigo }));
  const externoOptions = externos.map((x) => ({ value: String(x.id), label: x.nome }));

  return (
    <Modal opened={opened} onClose={onClose} title={initial ? "Editar trabalho" : "Novo trabalho"} size="xl">
      <Stack>
        <Grid>
          <Grid.Col span={{ base: 12, sm: 4 }}>
            <TextInput
              label="Referência"
              placeholder="ex.: 334.22"
              value={form.referencia}
              onChange={(e) => setForm({ ...form, referencia: e.currentTarget.value })}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 8 }}>
            <TextInput
              label="Cliente"
              value={form.cliente}
              onChange={(e) => setForm({ ...form, cliente: e.currentTarget.value })}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <TextInput
              label="Contacto"
              value={form.contacto}
              onChange={(e) => setForm({ ...form, contacto: e.currentTarget.value })}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6 }}>
            <TextInput
              label="Localidade"
              value={form.localidade}
              onChange={(e) => setForm({ ...form, localidade: e.currentTarget.value })}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 8 }}>
            <TextInput
              label="Endereço"
              value={form.endereco}
              onChange={(e) => setForm({ ...form, endereco: e.currentTarget.value })}
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 4 }}>
            <Select
              label="Intermediário"
              placeholder="—"
              clearable
              searchable
              data={intermediarios.map((i) => ({ value: String(i.id), label: i.nome }))}
              value={form.intermediario_id}
              onChange={(v) => setForm({ ...form, intermediario_id: v })}
            />
          </Grid.Col>
        </Grid>

        <Divider label="Especialidades" labelPosition="left" />

        <Stack gap="sm">
          {form.itens.map((item, idx) => (
            <Paper key={idx} withBorder p="sm" radius="md">
              <Group justify="space-between" mb="xs">
                <Title order={6}>Especialidade {idx + 1}</Title>
                <ActionIcon
                  color="red"
                  variant="subtle"
                  onClick={() => removeItem(idx)}
                  disabled={form.itens.length === 1}
                  title="Remover"
                >
                  <IconTrash size={16} />
                </ActionIcon>
              </Group>
              <Grid>
                <Grid.Col span={{ base: 12, sm: 4 }}>
                  <Select
                    label="Especialidade"
                    placeholder="—"
                    clearable
                    searchable
                    data={especOptions}
                    value={item.especialidade_id}
                    onChange={(v) => setItem(idx, { especialidade_id: v })}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 6, sm: 4 }}>
                  <NumberInput
                    label="Valor cliente (€)"
                    min={0}
                    decimalScale={2}
                    value={item.valor}
                    onChange={(v) => setItem(idx, { valor: v })}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 6, sm: 4 }}>
                  <Select
                    label="Externo"
                    placeholder="—"
                    clearable
                    searchable
                    data={externoOptions}
                    value={item.externo_id}
                    onChange={(v) => setItem(idx, { externo_id: v })}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 6, sm: 4 }}>
                  <NumberInput
                    label="Valor externo (€)"
                    min={0}
                    decimalScale={2}
                    value={item.valor_externo}
                    onChange={(v) => setItem(idx, { valor_externo: v })}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 6, sm: 4 }}>
                  <DateInput
                    label="Adjudicação"
                    valueFormat="DD/MM/YYYY"
                    clearable
                    value={item.data_adjudicacao}
                    onChange={(v) => setItem(idx, { data_adjudicacao: v })}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 6, sm: 4 }}>
                  <DateInput
                    label="Entrega"
                    valueFormat="DD/MM/YYYY"
                    clearable
                    value={item.data_entrega}
                    onChange={(v) => setItem(idx, { data_entrega: v })}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 12, sm: 4 }}>
                  <Select
                    label="Situação"
                    placeholder="—"
                    clearable
                    data={SITUACOES}
                    value={item.situacao}
                    onChange={(v) => setItem(idx, { situacao: (v as Situacao) ?? null })}
                  />
                </Grid.Col>
                <Grid.Col span={{ base: 12, sm: 8 }}>
                  <TextInput
                    label="Observações"
                    value={item.observacoes}
                    onChange={(e) => setItem(idx, { observacoes: e.currentTarget.value })}
                  />
                </Grid.Col>
              </Grid>
            </Paper>
          ))}
          <Group justify="space-between" align="flex-end">
            <Button variant="light" leftSection={<IconPlus size={16} />} onClick={addItem}>
              Adicionar especialidade
            </Button>
            <Select
              label="Aplicar situação a todas"
              placeholder="—"
              clearable
              data={SITUACOES}
              onChange={(v) => aplicarSituacaoATodas((v as Situacao) ?? null)}
              w={220}
            />
          </Group>
        </Stack>

        <Group justify="flex-end">
          <Text size="sm" c="dimmed">
            {form.itens.length} especialidade(s)
          </Text>
        </Group>

        <Button onClick={handleSubmit} loading={submitting}>
          Guardar
        </Button>
      </Stack>
    </Modal>
  );
}
