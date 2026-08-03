import type { InputHTMLAttributes } from 'react'

type InputProps = InputHTMLAttributes<HTMLInputElement> & { label?: string; error?: string }

export function Input({ label, error, id, className = '', ...props }: InputProps) {
  const inputId = id ?? props.name
  return <label className="grid gap-2 text-sm text-texto">{label && <span>{label}</span>}<input id={inputId} aria-invalid={Boolean(error)} aria-describedby={error ? `${inputId}-error` : undefined} className={['min-h-11 rounded-lg border border-contorno bg-superficie px-3.5 text-sm outline-none transition-[border-color,box-shadow] placeholder:text-texto-secundario/70 focus:border-texto focus:ring-2 focus:ring-texto/10 disabled:cursor-not-allowed disabled:opacity-50', error && 'border-erro focus:border-erro focus:ring-erro/10', className].filter(Boolean).join(' ')} {...props} />{error && <span id={`${inputId}-error`} role="alert" className="text-xs text-erro">{error}</span>}</label>
}
