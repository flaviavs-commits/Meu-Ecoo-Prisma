import type { SelectHTMLAttributes } from 'react'

type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & { label?: string; error?: string }

export function Select({ label, error, id, className = '', children, ...props }: SelectProps) {
  const selectId = id ?? props.name
  return <label className="grid gap-2 text-sm text-texto">{label && <span>{label}</span>}<select id={selectId} aria-invalid={Boolean(error)} className={['min-h-11 appearance-none rounded-lg border border-contorno bg-superficie px-3.5 text-sm outline-none transition-colors focus:border-texto focus:ring-2 focus:ring-texto/10 disabled:opacity-50', error && 'border-erro', className].filter(Boolean).join(' ')} {...props}>{children}</select>{error && <span role="alert" className="text-xs text-erro">{error}</span>}</label>
}
