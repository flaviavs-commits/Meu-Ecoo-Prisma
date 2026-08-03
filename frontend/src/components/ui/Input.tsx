import type { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  erro?: string
}

export function Input({ label, erro, id, ...props }: InputProps) {
  const inputId = id ?? props.name
  return (
    <label className="flex flex-col gap-2 text-sm text-texto" htmlFor={inputId}>
      <span>{label}</span>
      <input
        id={inputId}
        className="rounded-xl border border-contorno bg-superficie px-4 py-3 text-texto outline-none transition-colors placeholder:text-texto-secundario focus:border-marca focus:ring-2 focus:ring-marca/20"
        aria-invalid={Boolean(erro)}
        aria-describedby={erro ? `${inputId}-erro` : undefined}
        {...props}
      />
      {erro && <span id={`${inputId}-erro`} className="text-sm text-erro">{erro}</span>}
    </label>
  )
}
