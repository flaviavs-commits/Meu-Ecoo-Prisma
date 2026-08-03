import { useState, type ReactNode } from 'react'

type PopoverProps = { trigger: ReactNode; children: ReactNode; className?: string }

export function Popover({ trigger, children, className = '' }: PopoverProps) { const [open, setOpen] = useState(false); return <span className={['relative inline-flex', className].join(' ')}><button type="button" aria-expanded={open} onClick={() => setOpen((value) => !value)}>{trigger}</button>{open && <div role="dialog" className="absolute left-0 top-full z-20 mt-2 min-w-56 rounded-lg border border-contorno bg-superficie p-4 shadow-xl">{children}</div>}</span> }
