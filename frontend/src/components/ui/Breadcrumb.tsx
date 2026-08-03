import type { ReactNode } from 'react'

export interface BreadcrumbItem { label: ReactNode; href?: string }
export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) { return <nav aria-label="Navegação estrutural"><ol className="flex flex-wrap items-center gap-2 text-sm text-texto-secundario">{items.map((item, index) => <li key={index} className="flex items-center gap-2">{item.href ? <a href={item.href} className="hover:text-texto">{item.label}</a> : <span aria-current="page" className="font-semibold text-texto">{item.label}</span>}{index < items.length - 1 && <span aria-hidden="true">/</span>}</li>)}</ol></nav> }
