import type { ReactNode } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { SUAVE } from './movimento'

interface ItemAnimadoProps {
  children: ReactNode
  origem?: 'esquerda' | 'direita'
  className?: string
}

/** Filho de ListaAnimada com entrada lateral inspirada na refração. */
export function ItemAnimado({
  children,
  origem = 'esquerda',
  className = '',
}: ItemAnimadoProps) {
  const reduzido = useReducedMotion()

  if (reduzido) {
    return <div className={className}>{children}</div>
  }

  const lado = origem === 'esquerda' ? -1 : 1

  return (
    <motion.div
      className={className}
      variants={{
        oculto: {
          opacity: 0,
          x: 28 * lado,
          skewY: 1.5 * lado,
          scale: 0.98,
        },
        visivel: { opacity: 1, x: 0, skewY: 0, scale: 1 },
      }}
      transition={{ duration: 0.65, ease: SUAVE }}
    >
      {children}
    </motion.div>
  )
}
