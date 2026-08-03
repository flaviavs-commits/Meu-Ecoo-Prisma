import type { ReactNode } from 'react'
import { Overlay } from './Overlay'

type ToastProps = { open: boolean; children: ReactNode; tone?: 'neutral' | 'success' | 'danger'; onClose?: () => void }

export function Toast({ open, children, tone = 'neutral', onClose }: ToastProps) { if (!open) return null; const colors = { neutral: 'border-contorno', success: 'border-sucesso/40', danger: 'border-erro/40' }; return <Overlay><div role="status" className={['fixed bottom-5 right-5 z-50 flex max-w-sm items-center gap-4 rounded-lg border bg-superficie px-4 py-3 text-sm shadow-xl', colors[tone]].join(' ')}>{children}{onClose && <button type="button" aria-label="Fechar aviso" onClick={onClose} className="text-texto-secundario">×</button>}</div></Overlay> }
