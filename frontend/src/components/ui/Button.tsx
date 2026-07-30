import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  /** Renderiza como <a> quando informado. Util para CTA que navega. */
  href?: string
  children: ReactNode
}

const porVariante: Record<Variant, string> = {
  primary: 'bg-graphite text-cream hover:bg-marca',
  secondary:
    'bg-transparent text-texto border border-texto/30 hover:border-texto/70',
  ghost: 'text-texto hover:text-marca',
}

const porTamanho: Record<Size, string> = {
  sm: 'text-xs px-5 py-2.5',
  md: 'text-xs px-7 py-3.5',
  lg: 'text-sm px-9 py-4',
}

/**
 * Botao base do design system.
 * Variantes explícitas por prop, conforme DESIGN_SYSTEM_FRONTEND.md seção 5.
 */
export function Button({
  variant = 'primary',
  size = 'md',
  href,
  children,
  className = '',
  ...props
}: ButtonProps) {
  const estilo = [
    // Pill totalmente arredondado, rótulo em caixa alta com tracking largo
    'inline-flex items-center justify-center gap-2 rounded-full',
    'fonte-display font-bold uppercase tracking-[0.08em]',
    'transition-colors duration-200 ease-out',
    'disabled:opacity-50 disabled:pointer-events-none',
    porVariante[variant],
    porTamanho[size],
    className,
  ].join(' ')

  if (href) {
    return (
      <a href={href} className={estilo}>
        {children}
      </a>
    )
  }

  return (
    <button className={estilo} {...props}>
      {children}
    </button>
  )
}
