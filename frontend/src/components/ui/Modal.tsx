import { useEffect, useId, useRef, type ReactNode } from 'react'
import { Overlay } from './Overlay'

type ModalProps = { open: boolean; title: string; children: ReactNode; onClose: () => void; size?: 'sm' | 'md' | 'lg' }

const SELETOR_FOCAVEL = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])'

export function Modal({ open, title, children, onClose, size = 'md' }: ModalProps) {
  const tituloId = useId()
  const dialogoRef = useRef<HTMLElement>(null)
  useEffect(() => {
    if (!open) return
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const anterior = document.activeElement as HTMLElement | null
    dialogoRef.current?.focus()
    function aoTeclar(event: KeyboardEvent) {
      if (event.key === 'Escape') { onClose(); return }
      if (event.key !== 'Tab') return
      const focaveis = dialogoRef.current?.querySelectorAll<HTMLElement>(SELETOR_FOCAVEL)
      if (!focaveis || focaveis.length === 0) return
      const primeiro = focaveis[0]
      const ultimo = focaveis[focaveis.length - 1]
      if (event.shiftKey && document.activeElement === primeiro) { event.preventDefault(); ultimo.focus() }
      else if (!event.shiftKey && document.activeElement === ultimo) { event.preventDefault(); primeiro.focus() }
    }
    window.addEventListener('keydown', aoTeclar)
    return () => {
      document.body.style.overflow = previous
      window.removeEventListener('keydown', aoTeclar)
      anterior?.focus()
    }
  }, [open, onClose])
  if (!open) return null
  return <Overlay><div className="fixed inset-0 z-50 grid place-items-center bg-texto/45 p-4 backdrop-blur-sm" onMouseDown={(event) => event.target === event.currentTarget && onClose()}><section ref={dialogoRef} tabIndex={-1} role="dialog" aria-modal="true" aria-labelledby={tituloId} className={['w-full rounded-xl border border-contorno bg-superficie p-6 shadow-2xl outline-none', size === 'sm' && 'max-w-md', size === 'md' && 'max-w-xl', size === 'lg' && 'max-w-3xl'].join(' ')}><div className="flex items-start justify-between gap-4"><h2 id={tituloId} className="font-display text-xl font-bold">{title}</h2><button type="button" aria-label="Fechar" onClick={onClose} className="grid h-9 w-9 place-items-center rounded-lg text-texto-secundario hover:bg-superficie-alt">×</button></div><div className="mt-5">{children}</div></section></div></Overlay>
}
