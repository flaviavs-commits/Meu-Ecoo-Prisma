interface ErrorStateProps {
  title?: string
  message?: string
  retry?: () => void
  retryLabel?: string
  className?: string
}

/** Estado de erro com mensagem segura e retry opcional. */
export function ErrorState({
  title = 'Não foi possível carregar',
  message = 'Tente novamente em instantes.',
  retry,
  retryLabel = 'Tentar novamente',
  className = '',
}: ErrorStateProps) {
  return (
    <div
      className={['flex min-h-32 flex-col items-center justify-center gap-2 text-center', className].join(' ')}
      role="alert"
    >
      <h2 className="fonte-display text-lg">{title}</h2>
      <p className="max-w-md text-sm text-texto-secundario">{message}</p>
      {retry && (
        <button
          type="button"
          className="mt-2 rounded-full border border-texto/30 px-5 py-2.5 text-xs font-bold tracking-[0.08em] text-texto uppercase transition-colors hover:border-texto/70"
          onClick={retry}
        >
          {retryLabel}
        </button>
      )}
    </div>
  )
}
