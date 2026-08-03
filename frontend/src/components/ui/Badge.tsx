import type { HTMLAttributes } from 'react'

type BadgeProps = HTMLAttributes<HTMLSpanElement> & { tone?: 'neutral' | 'success' | 'warning' | 'danger' }

export function Badge({ tone = 'neutral', className = '', ...props }: BadgeProps) {
  const tones = { neutral: 'bg-superficie-alt text-texto-secundario', success: 'bg-sucesso/10 text-sucesso', warning: 'bg-alerta/10 text-alerta', danger: 'bg-erro/10 text-erro' }
  return <span className={['inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold', tones[tone], className].join(' ')} {...props} />
}
