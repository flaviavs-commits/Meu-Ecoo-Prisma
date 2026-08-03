import type { ReactNode } from 'react'

type TooltipProps = { label: string; children: ReactNode }

export function Tooltip({ label, children }: TooltipProps) { return <span className="group relative inline-flex">{children}<span role="tooltip" className="pointer-events-none absolute bottom-full left-1/2 z-20 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-texto px-2.5 py-1.5 text-xs text-superficie opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">{label}</span></span> }
