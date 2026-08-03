import { useEffect, type ReactNode } from 'react'
import { Overlay } from './Overlay'

type ModalProps = { open: boolean; title: string; children: ReactNode; onClose: () => void; size?: 'sm' | 'md' | 'lg' }

export function Modal({ open, title, children, onClose, size = 'md' }: ModalProps) {
  useEffect(() => { if (!open) return; const previous = document.body.style.overflow; document.body.style.overflow = 'hidden'; const close = (event: KeyboardEvent) => event.key === 'Escape' && onClose(); window.addEventListener('keydown', close); return () => { document.body.style.overflow = previous; window.removeEventListener('keydown', close) } }, [open, onClose])
  if (!open) return null
  return <Overlay><div className="fixed inset-0 z-50 grid place-items-center bg-texto/45 p-4 backdrop-blur-sm" onMouseDown={(event) => event.target === event.currentTarget && onClose()}><section role="dialog" aria-modal="true" aria-labelledby="modal-title" className={['w-full rounded-xl border border-contorno bg-superficie p-6 shadow-2xl', size === 'sm' && 'max-w-md', size === 'md' && 'max-w-xl', size === 'lg' && 'max-w-3xl'].join(' ')}><div className="flex items-start justify-between gap-4"><h2 id="modal-title" className="font-display text-xl font-bold">{title}</h2><button type="button" aria-label="Fechar" onClick={onClose} className="grid h-9 w-9 place-items-center rounded-lg text-texto-secundario hover:bg-superficie-alt">×</button></div><div className="mt-5">{children}</div></section></div></Overlay>
}
