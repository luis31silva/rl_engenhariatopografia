import { useState } from "react";
import { Group, Text } from "@mantine/core";

import { LogoMark } from "./LogoMark";

interface Props {
  /** "horizontal" (cabeçalho) usa logo.png; "vertical" (login) usa logo-vertical.png. */
  variant?: "horizontal" | "vertical";
  height?: number;
  /** Cor do texto do fallback (útil sobre fundo escuro). */
  textColor?: string;
}

/**
 * Logótipo da empresa. Tenta carregar o ficheiro oficial de /public;
 * se não existir, mostra o monograma SVG + nome (fallback com a identidade da marca).
 *
 *   frontend/public/logo.png           -> variante horizontal (cabeçalho)
 *   frontend/public/logo-vertical.png  -> variante vertical (login)
 */
export function Logo({ variant = "horizontal", height = 40, textColor }: Props) {
  const [erro, setErro] = useState(false);
  const src = variant === "vertical" ? "/logo-vertical.png" : "/logo.png";

  if (erro) {
    // Fallback vertical: monograma por cima, nome por baixo.
    if (variant === "vertical") {
      return (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <LogoMark size={height * 0.7} />
          <div style={{ textAlign: "center", lineHeight: 1.1 }}>
            <Text fw={800} c={textColor ?? "salvia.6"} style={{ fontSize: height * 0.16, letterSpacing: 2, textTransform: "uppercase" }}>
              Engenharia
            </Text>
            <Text fw={800} c={textColor ?? "petroleo.7"} style={{ fontSize: height * 0.16, letterSpacing: 2, textTransform: "uppercase" }}>
              Topografia
            </Text>
            <Text fw={600} c={textColor ?? "dimmed"} style={{ fontSize: height * 0.09, letterSpacing: 1.5, textTransform: "uppercase" }}>
              Projetos e Levantamentos
            </Text>
          </div>
        </div>
      );
    }
    // Fallback horizontal: monograma + nome ao lado.
    return (
      <Group gap="xs" wrap="nowrap">
        <LogoMark size={height} />
        <div style={{ lineHeight: 1.05 }}>
          <Text fw={800} c={textColor ?? "salvia.4"} style={{ letterSpacing: 0.5, fontSize: height * 0.4 }}>
            RL
          </Text>
          <Text fw={600} c={textColor ?? "gray.5"} style={{ fontSize: height * 0.22, textTransform: "uppercase", letterSpacing: 1 }}>
            Eng &amp; Topografia
          </Text>
        </div>
      </Group>
    );
  }

  return (
    <img
      src={src}
      alt="RL Engenharia & Topografia"
      style={{
        height,
        width: "auto",
        maxWidth: "100%",
        objectFit: "contain",
        display: "block",
      }}
      onError={() => setErro(true)}
    />
  );
}
