import type { InputHTMLAttributes } from 'react'

type SearchProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> & { label?: string }

export function Search({ label = 'Buscar', className = '', ...props }: SearchProps) {
  return <label className="relative block"><span className="sr-only">{label}</span><span aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-texto-secundario">⌕</span><input type="search" aria-label={label} className={['min-h-11 w-full rounded-lg border border-contorno bg-superficie pl-9 pr-3.5 text-sm outline-none transition-colors focus:border-texto focus:ring-2 focus:ring-texto/10 placeholder:text-texto-secundario/70', className].join(' ')} {...props} /></label>
}
