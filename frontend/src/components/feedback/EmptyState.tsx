import type { ReactNode } from 'react'

interface EmptyStateProps {
  title: string
  message?: string
  action?: ReactNode
  className?: string
}

/** Estado vazio para uma coleção sem dados. */
export function EmptyState({
  title,
  message,
  action,
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={['flex min-h-40 flex-col items-center justify-center gap-2 text-center', className].join(' ')}
      role="status"
    >
      <h2 className="fonte-display text-lg">{title}</h2>
      {message && <p className="max-w-md text-sm text-texto-secundario">{message}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
