interface LoadingStateProps {
  label?: string
  className?: string
}

/** Estado de carregamento acessível para telas e regiões assíncronas. */
export function LoadingState({
  label = 'Carregando…',
  className = '',
}: LoadingStateProps) {
  return (
    <div
      className={['flex min-h-32 items-center justify-center gap-3 text-texto-secundario', className].join(' ')}
      role="status"
      aria-live="polite"
    >
      <span
        aria-hidden="true"
        className="h-4 w-4 animate-spin rounded-full border-2 border-contorno border-t-texto"
      />
      <span>{label}</span>
    </div>
  )
}
