import type { ReactNode } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { SUAVE } from './movimento'

interface AoEntrarProps {
  children: ReactNode
  atraso?: number
  deslocamento?: number
  className?: string
}

/** Revela o conteúdo quando ele entra na viewport. */
export function AoEntrar({
  children,
  atraso = 0,
  deslocamento = 16,
  className = '',
}: AoEntrarProps) {
  const reduzido = useReducedMotion()

  if (reduzido) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: deslocamento }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.5, delay: atraso, ease: SUAVE }}
    >
      {children}
    </motion.div>
  )
}
