import { useEffect, useRef, useState, type ReactNode } from 'react'

type PopoverProps = { trigger: ReactNode; children: ReactNode; className?: string }

export function Popover({ trigger, children, className = '' }: PopoverProps) {
  const [open, setOpen] = useState(false)
  const raiz = useRef<HTMLSpanElement>(null)
  useEffect(() => {
    if (!open) return
    function fechar(event: MouseEvent | KeyboardEvent) {
      if (event instanceof KeyboardEvent) { if (event.key === 'Escape') setOpen(false); return }
      if (!raiz.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', fechar)
    document.addEventListener('keydown', fechar)
    return () => { document.removeEventListener('mousedown', fechar); document.removeEventListener('keydown', fechar) }
  }, [open])
  return <span ref={raiz} className={['relative inline-flex', className].join(' ')}><button type="button" aria-expanded={open} onClick={() => setOpen((value) => !value)}>{trigger}</button>{open && <div role="dialog" className="absolute left-0 top-full z-20 mt-2 min-w-56 rounded-lg border border-contorno bg-superficie p-4 shadow-xl">{children}</div>}</span>
}
