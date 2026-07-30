interface LogoProps {
  /** Tamanho do simbolo em px. */
  tamanho?: number
  className?: string
}

/**
 * Simbolo oficial do Prisma (prisma-logo-minimal.svg): losango com a
 * aresta central e o "V" da base, sugerindo a luz se dividindo dentro
 * do prisma. Coordenadas convertidas do viewBox original (1254x1254).
 *
 * O viewBox e recortado nos limites reais do desenho (x: 6.35-25.65,
 * y: 6.38-25.37), com uma margem simetrica de 1.2 - nao 0-32 inteiro.
 * Um viewBox maior que o desenho deixa folga desigual entre o traco e
 * a caixa do SVG; ao lado do texto em caixa alta (sem descendentes,
 * mais compacto verticalmente), essa folga lia como o triangulo
 * "flutuando" acima da linha do texto em vez de alinhado com ele.
 */
export function Logo({ tamanho = 28, className = '' }: LogoProps) {
  return (
    <svg
      width={tamanho}
      height={tamanho}
      viewBox="5.15 5.18 21.8 21.39"
      fill="none"
      role="img"
      aria-label="Prisma"
      className={className}
    >
      <g
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M16 6.38 6.35 21.56 16 25.37l9.65-3.81Z" />
        <path d="M16 6.38V25.37" />
        <path d="M6.35 21.56 16 17.51l9.65 4.05" />
      </g>
    </svg>
  )
}

/** Logo com nome, para header e rodapé. */
export function LogoComNome({ className = '' }: { className?: string }) {
  return (
    <span className={['inline-flex items-center gap-2', className].join(' ')}>
      <Logo tamanho={30} className="text-texto" />
      <span className="fonte-display text-xl font-bold tracking-[0.16em] uppercase">
        Prisma
      </span>
    </span>
  )
}
