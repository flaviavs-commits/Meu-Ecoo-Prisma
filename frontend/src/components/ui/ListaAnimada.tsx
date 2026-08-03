import type { ReactNode } from 'react'
import { motion, useReducedMotion } from 'motion/react'

interface ListaAnimadaProps {
  children: ReactNode
  intervalo?: number
  className?: string
}

/** Escalona a entrada dos filhos diretos. */
export function ListaAnimada({
  children,
  intervalo = 0.08,
  className = '',
}: ListaAnimadaProps) {
  const reduzido = useReducedMotion()

  if (reduzido) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      className={className}
      initial="oculto"
      whileInView="visivel"
      viewport={{ once: true, margin: '-80px' }}
      variants={{
        visivel: { transition: { staggerChildren: intervalo } },
      }}
    >
      {children}
    </motion.div>
  )
}
