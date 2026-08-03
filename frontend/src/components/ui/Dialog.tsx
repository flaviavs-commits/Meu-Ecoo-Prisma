import type { ReactNode } from 'react'
import { Modal } from './Modal'

type DialogProps = { open: boolean; title: string; description?: string; confirmLabel?: string; onConfirm: () => void; onClose: () => void; children?: ReactNode }

export function Dialog({ open, title, description, confirmLabel = 'Confirmar', onConfirm, onClose, children }: DialogProps) {
  return <Modal open={open} title={title} onClose={onClose} size="sm"><div className="grid gap-5"><p className="text-sm leading-relaxed text-texto-secundario">{description}</p>{children}<div className="flex flex-col-reverse justify-end gap-2 sm:flex-row"><button type="button" className="min-h-11 rounded-lg border border-contorno px-4 text-sm font-semibold hover:bg-superficie-alt" onClick={onClose}>Cancelar</button><button type="button" className="min-h-11 rounded-lg bg-primaria px-4 text-sm font-semibold text-superficie hover:bg-primaria-forte" onClick={onConfirm}>{confirmLabel}</button></div></div></Modal>
}
