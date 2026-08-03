import { useId, useState, type ReactNode } from 'react'

export interface TabItem { id: string; label: ReactNode; content: ReactNode; disabled?: boolean }
type TabsProps = { items: TabItem[]; defaultValue?: string; className?: string }

export function Tabs({ items, defaultValue, className = '' }: TabsProps) {
  const baseId = useId(); const [active, setActive] = useState(defaultValue ?? items[0]?.id)
  const index = Math.max(0, items.findIndex((item) => item.id === active))
  function move(direction: number) { const next = (index + direction + items.length) % items.length; if (!items[next]?.disabled) setActive(items[next].id) }
  const current = items.find((item) => item.id === active) ?? items[0]
  if (!current) return null
  return <div className={['grid gap-5', className].join(' ')}><div className="flex gap-1 overflow-x-auto border-b border-contorno" role="tablist" onKeyDown={(event) => { if (event.key === 'ArrowRight') move(1); if (event.key === 'ArrowLeft') move(-1) }}>{items.map((item) => <button key={item.id} type="button" role="tab" aria-selected={item.id === current.id} aria-controls={`${baseId}-${item.id}`} tabIndex={item.id === current.id ? 0 : -1} disabled={item.disabled} onClick={() => setActive(item.id)} className={['min-h-11 shrink-0 border-b-2 px-3 text-sm font-semibold transition-colors', item.id === current.id ? 'border-texto text-texto' : 'border-transparent text-texto-secundario hover:text-texto', item.disabled && 'cursor-not-allowed opacity-40'].filter(Boolean).join(' ')}>{item.label}</button>)}</div><div id={`${baseId}-${current.id}`} role="tabpanel" tabIndex={0}>{current.content}</div></div>
}
