import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Center,
  Paper,
  PasswordInput,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";

import { useAuth } from "../auth/AuthContext";
import { Logo } from "../components/Logo";
import { extractError } from "../utils/errors";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErro(null);
    setLoading(true);
    try {
      await login(username, password);
      navigate("/", { replace: true });
    } catch (err) {
      setErro(extractError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Center mih="100vh" p="md" bg="carvao.9">
      <Paper shadow="xl" p="xl" radius="lg" w={380} bg="white">
        <form onSubmit={handleSubmit}>
          <Stack>
            <Stack gap={12} align="center" mb="xs">
              <Box
                p="xl"
                style={{
                  background: "#000000",
                  borderRadius: 20,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Logo variant="vertical" height={160} textColor="white" />
              </Box>
              <Text c="dimmed" size="sm">
                Inicie sessão para continuar
              </Text>
            </Stack>
            <TextInput
              label="Utilizador"
              required
              value={username}
              onChange={(e) => setUsername(e.currentTarget.value)}
            />
            <PasswordInput
              label="Password"
              required
              value={password}
              onChange={(e) => setPassword(e.currentTarget.value)}
            />
            {erro && (
              <Text c="red" size="sm">
                {erro}
              </Text>
            )}
            <Button type="submit" loading={loading} fullWidth>
              Entrar
            </Button>
          </Stack>
        </form>
      </Paper>
    </Center>
  );
}
