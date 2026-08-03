import type { ButtonHTMLAttributes } from 'react'

type ChipProps = ButtonHTMLAttributes<HTMLButtonElement> & { selected?: boolean }

export function Chip({ selected = false, className = '', ...props }: ChipProps) {
  return <button type="button" aria-pressed={selected} className={['min-h-9 rounded-full border px-3.5 text-xs font-semibold transition-colors', selected ? 'border-texto bg-texto text-superficie' : 'border-contorno bg-superficie text-texto-secundario hover:border-texto/60 hover:text-texto', className].join(' ')} {...props} />
}
