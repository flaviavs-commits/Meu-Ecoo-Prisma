import type {
  AnchorHTMLAttributes,
  ButtonHTMLAttributes,
  ReactNode,
} from 'react'

type Variant = 'primary' | 'secondary' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

interface ButtonVisualProps {
  variant?: Variant
  size?: Size
  children: ReactNode
  className?: string
}

type ButtonElementProps = ButtonHTMLAttributes<HTMLButtonElement> & { href?: never }
type ButtonLinkProps = AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }
type ButtonProps = ButtonVisualProps & (ButtonElementProps | ButtonLinkProps)

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
export function Button(props: ButtonProps) {
  const {
    variant = 'primary',
    size = 'md',
    children,
    className = '',
  } = props

  const estilo = [
    // Pill totalmente arredondado, rótulo em caixa alta com tracking largo
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-full whitespace-nowrap',
    'fonte-display font-bold uppercase tracking-[0.08em]',
    'transition-colors duration-200 ease-out',
    'disabled:opacity-50 disabled:pointer-events-none',
    porVariante[variant],
    porTamanho[size],
    className,
  ].join(' ')

  if ('href' in props) {
    const linkProps = props as ButtonVisualProps & ButtonLinkProps
    const { href, variant: _variant, size: _size, children: _children, className: _className, ...anchorProps } = linkProps
    return (
      <a href={href} className={estilo} {...anchorProps}>
        {children}
      </a>
    )
  }

  const buttonProps = props as ButtonVisualProps & ButtonElementProps
  const { variant: _variant, size: _size, children: _children, className: _className, ...elementProps } = buttonProps
  return (
    <button className={estilo} {...elementProps}>
      {children}
    </button>
  )
}
