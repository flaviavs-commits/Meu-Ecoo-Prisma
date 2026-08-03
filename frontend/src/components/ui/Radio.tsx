import type { InputHTMLAttributes } from 'react'

type RadioProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> & { label: string }

export function Radio({ label, className = '', ...props }: RadioProps) {
  return <label className="inline-flex min-h-11 cursor-pointer items-center gap-3 text-sm text-texto"><input type="radio" className={['h-4 w-4 accent-primaria', className].filter(Boolean).join(' ')} {...props} /><span>{label}</span></label>
}
