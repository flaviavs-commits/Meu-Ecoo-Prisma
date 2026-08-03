import type { TextareaHTMLAttributes } from 'react'

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & { label?: string; error?: string }

export function Textarea({ label, error, id, className = '', ...props }: TextareaProps) {
  const textareaId = id ?? props.name
  return <label className="grid gap-2 text-sm text-texto">{label && <span>{label}</span>}<textarea id={textareaId} aria-invalid={Boolean(error)} aria-describedby={error ? `${textareaId}-error` : undefined} className={['min-h-28 resize-y rounded-lg border border-contorno bg-superficie px-3.5 py-3 text-sm outline-none transition-[border-color,box-shadow] placeholder:text-texto-secundario/70 focus:border-texto focus:ring-2 focus:ring-texto/10 disabled:cursor-not-allowed disabled:opacity-50', error && 'border-erro focus:border-erro focus:ring-erro/10', className].filter(Boolean).join(' ')} {...props} />{error && <span id={`${textareaId}-error`} role="alert" className="text-xs text-erro">{error}</span>}</label>
}
