import { createTheme, type MantineColorsTuple } from "@mantine/core";

// Paleta inspirada no logótipo RL Engenharia & Topografia:
// verde-sálvia (claro) + verde-petróleo (escuro) sobre fundo escuro.

// Verde-petróleo (cor primária) — botões, links, acentos.
const petroleo: MantineColorsTuple = [
  "#e6f2ef",
  "#cfe3de",
  "#a3c8c0",
  "#74ac9f",
  "#4f9585",
  "#378675",
  "#297f6d",
  "#1a6d5c",
  "#0c6151",
  "#005344",
];

// Verde-sálvia (cor de destaque/secundária).
const salvia: MantineColorsTuple = [
  "#f2f7ec",
  "#e4ecda",
  "#c8d9b4",
  "#aac58b",
  "#91b568",
  "#82ab51",
  "#79a544",
  "#679036",
  "#5a802d",
  "#4a6f20",
];

// Tons escuros da marca (para a barra lateral e o cabeçalho).
const carvao: MantineColorsTuple = [
  "#c9ccd1",
  "#a6abb3",
  "#848a95",
  "#646b78",
  "#4a515d",
  "#343a45",
  "#272c35",
  "#1d222a",
  "#161a20",
  "#111417",
];

export const theme = createTheme({
  primaryColor: "petroleo",
  colors: {
    petroleo,
    salvia,
    carvao,
  },
  primaryShade: { light: 7, dark: 5 },
  defaultRadius: "md",
  fontFamily:
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
  headings: {
    fontWeight: "700",
  },
});
