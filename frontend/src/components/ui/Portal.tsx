import type { ReactNode, RefObject } from 'react'
import { motion, useReducedMotion, useScroll, useTransform } from 'motion/react'

interface PortalProps {
  children: ReactNode
  alvo: RefObject<HTMLElement | null>
  className?: string
}

/** Faz o conteúdo emergir suavemente ao entrar na seção. */
export function Portal({ children, alvo, className = '' }: PortalProps) {
  const reduzido = useReducedMotion()

  const { scrollYProgress } = useScroll({
    target: alvo,
    offset: ['start end', 'center center'],
  })

  const escala = useTransform(scrollYProgress, [0, 1], [0.975, 1])
  const opacidade = useTransform(scrollYProgress, [0, 0.6], [0.5, 1])

  if (reduzido) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      className={className}
      style={{ scale: escala, opacity: opacidade, willChange: 'transform' }}
    >
      {children}
    </motion.div>
  )
}
