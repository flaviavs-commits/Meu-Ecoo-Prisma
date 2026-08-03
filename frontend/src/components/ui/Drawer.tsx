import type { ReactNode } from 'react'
import { Modal } from './Modal'

type DrawerProps = { open: boolean; title: string; children: ReactNode; onClose: () => void }

export function Drawer({ open, title, children, onClose }: DrawerProps) { return <Modal open={open} title={title} onClose={onClose} size="lg">{children}</Modal> }
