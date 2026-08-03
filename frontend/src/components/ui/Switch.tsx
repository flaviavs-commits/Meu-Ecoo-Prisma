import type { InputHTMLAttributes } from 'react'

type SwitchProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> & { label: string }

export function Switch({ label, className = '', ...props }: SwitchProps) {
  return <label className="inline-flex min-h-11 cursor-pointer items-center gap-3 text-sm text-texto"><input type="checkbox" role="switch" className="peer sr-only" {...props} /><span aria-hidden="true" className={['relative h-6 w-10 rounded-full bg-contorno-forte transition-colors peer-checked:bg-primaria peer-focus-visible:ring-2 peer-focus-visible:ring-primaria/30 after:absolute after:left-1 after:top-1 after:h-4 after:w-4 after:rounded-full after:bg-superficie after:shadow-sm after:transition-transform peer-checked:after:translate-x-4', className].filter(Boolean).join(' ')} /><span>{label}</span></label>
}
