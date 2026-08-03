import { useState, type KeyboardEvent } from 'react'

type ComboboxProps = { label?: string; options: string[]; value?: string; onChange?: (value: string) => void; placeholder?: string; className?: string }

export function Combobox({ label = 'Selecionar', options, value = '', onChange, placeholder = 'Digite para buscar', className = '' }: ComboboxProps) {
  const [query, setQuery] = useState(value); const [open, setOpen] = useState(false)
  const filtered = options.filter((option) => option.toLocaleLowerCase().includes(query.toLocaleLowerCase()))
  function choose(option: string) { setQuery(option); setOpen(false); onChange?.(option) }
  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) { if (event.key === 'Escape') setOpen(false); if (event.key === 'Enter' && filtered[0]) { event.preventDefault(); choose(filtered[0]) } }
  return <div className={['relative grid gap-2 text-sm text-texto', className].join(' ')}><label htmlFor="combobox-input">{label}</label><input id="combobox-input" role="combobox" aria-expanded={open} aria-controls="combobox-options" aria-autocomplete="list" value={query} placeholder={placeholder} onFocus={() => setOpen(true)} onChange={(event) => { setQuery(event.target.value); setOpen(true) }} onKeyDown={handleKeyDown} className="min-h-11 rounded-lg border border-contorno bg-superficie px-3.5 text-sm outline-none transition-colors focus:border-texto focus:ring-2 focus:ring-texto/10" />{open && filtered.length > 0 && <ul id="combobox-options" role="listbox" className="absolute inset-x-0 top-full z-20 mt-2 max-h-56 overflow-auto rounded-lg border border-contorno bg-superficie p-1 shadow-xl">{filtered.map((option) => <li key={option} role="option" aria-selected={option === query}><button type="button" className="min-h-10 w-full rounded-md px-3 text-left text-sm hover:bg-superficie-alt" onMouseDown={(event) => event.preventDefault()} onClick={() => choose(option)}>{option}</button></li>)}</ul>}</div>
}
