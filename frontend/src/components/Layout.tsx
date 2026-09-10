import { AppShell, Burger, Group, NavLink, UnstyledButton } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  IconBriefcase,
  IconCategory,
  IconChartBar,
  IconLogout,
  IconUsers,
  IconUserShare,
} from "@tabler/icons-react";

import { useAuth } from "../auth/AuthContext";
import { Logo } from "./Logo";
import classes from "./Layout.module.css";

const navItems = [
  { to: "/", label: "Trabalhos", icon: IconBriefcase },
  { to: "/dashboard", label: "Relatório de Contas", icon: IconChartBar },
  { to: "/especialidades", label: "Especialidades", icon: IconCategory },
  { to: "/intermediarios", label: "Intermediários", icon: IconUserShare },
  { to: "/externos", label: "Externos", icon: IconUsers },
];

export function Layout() {
  const [opened, { toggle, close }] = useDisclosure();
  const location = useLocation();
  const navigate = useNavigate();
  const { logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <AppShell
      header={{ height: 72 }}
      navbar={{ width: 250, breakpoint: "sm", collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header bg="carvao.9" withBorder={false}>
        <Group h="100%" px="md" gap="sm">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" color="white" />
          <Logo height={52} />
        </Group>
      </AppShell.Header>

      <AppShell.Navbar
        p="md"
        bg="carvao.9"
        withBorder={false}
        style={{ display: "flex", flexDirection: "column" }}
      >
        <div style={{ flex: 1 }}>
          {navItems.map((item) => {
            const ativo = location.pathname === item.to;
            return (
              <NavLink
                key={item.to}
                component={Link}
                to={item.to}
                label={item.label}
                leftSection={<item.icon size={18} />}
                active={ativo}
                color="salvia"
                variant="filled"
                onClick={close}
                className={ativo ? undefined : classes.navLink}
              />
            );
          })}
        </div>
        <UnstyledButton onClick={handleLogout} className={classes.logout}>
          <IconLogout size={18} />
          <span>Terminar sessão</span>
        </UnstyledButton>
      </AppShell.Navbar>

      <AppShell.Main bg="gray.0">
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
