/**
 * Monograma "RL" desenhado em SVG, inspirado no logótipo da RL Engenharia & Topografia.
 * Usado como fallback e como ícone da marca dentro da aplicação.
 * Cores: sálvia (#a7c17a) e petróleo (#2f6f6a) sobre fundo escuro (#111).
 */
export function LogoMark({ size = 40, rounded = true }: { size?: number; rounded?: boolean }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="RL"
    >
      <rect width="100" height="100" rx={rounded ? 16 : 0} fill="#111417" />

      {/* Arco superior (sálvia) e inferior (petróleo), formando o círculo aberto. */}
      <path
        d="M50 14 A36 36 0 0 1 86 50"
        fill="none"
        stroke="#a7c17a"
        strokeWidth="9"
        strokeLinecap="square"
      />
      <path
        d="M14 50 A36 36 0 0 0 50 86"
        fill="none"
        stroke="#2f6f6a"
        strokeWidth="9"
        strokeLinecap="square"
      />

      {/* Bloco do "R" (sálvia). */}
      <path
        d="M22 30 h20 a10 10 0 0 1 0 20 h-6 l10 20 h-12 l-9 -18 v18 h-13 z"
        fill="#a7c17a"
      />
      {/* Contra-forma do R (fundo). */}
      <rect x="30" y="38" width="9" height="6" fill="#111417" />

      {/* Haste do "L" (petróleo), sobreposta. */}
      <path d="M52 28 h11 v30 h16 v12 h-27 z" fill="#2f6f6a" />
    </svg>
  );
}
