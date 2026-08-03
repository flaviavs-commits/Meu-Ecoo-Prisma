import type { ReactNode } from 'react'
import { Popover } from './Popover'

type DropdownProps = { label: ReactNode; children: ReactNode }

export function Dropdown({ label, children }: DropdownProps) { return <Popover trigger={<span className="inline-flex min-h-10 items-center rounded-lg border border-contorno px-3 text-sm font-semibold hover:bg-superficie-alt">{label}</span>}>{children}</Popover> }
