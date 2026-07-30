import type { ReactNode } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { SUAVE } from './movimento'

/**
 * Base de animação do Prisma.
 *
 * Regras que valem para todo movimento nesta landing:
 *
 * 1. ACESSIBILIDADE NÃO É OPCIONAL. Todo componente daqui consulta
 *    `useReducedMotion`. Quem pediu menos movimento no sistema recebe
 *    o conteúdo estático, nunca uma tela vazia - por isso o estado
 *    final é sempre visível, e só a transição é suprimida.
 *
 * 2. ANIMAÇÃO ORIENTA, NÃO DECORA (DESIGN_SYSTEM_FRONTEND.md, seção 9).
 *    Entrada suave ao rolar e resposta a hover: sim. Movimento
 *    contínuo competindo com o texto: não.
 *
 * 3. O CONTEÚDO NUNCA DEPENDE DA ANIMAÇÃO PARA EXISTIR. Se o JS
 *    falhar, o texto continua lá - as variantes animam opacidade e
 *    deslocamento, jamais `display`.
 */

interface AoEntrarProps {
  children: ReactNode
  /** Atraso em segundos. Use para escalonar itens vizinhos. */
  atraso?: number
  /** Deslocamento inicial em px. Negativo sobe, positivo desce. */
  deslocamento?: number
  className?: string
}

/**
 * Revela o conteúdo quando ele entra na viewport.
 * `once` evita que a animação repita a cada rolagem, o que vira ruído.
 */
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

interface ListaAnimadaProps {
  children: ReactNode
  /** Intervalo entre os filhos, em segundos. */
  intervalo?: number
  className?: string
}

/**
 * Escalona a entrada dos filhos diretos.
 * Envolva cada filho em <ItemAnimado> para que herdem as variantes.
 */
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

/**
 * Filho de <ListaAnimada>. Sozinho não anima nada.
 *
 * O movimento é de REFRAÇÃO, não o fade-up genérico: o item chega
 * deslocado lateralmente e levemente inclinado, como um raio que
 * atravessa o prisma e se endireita ao sair. `origem` define de que
 * lado ele entra - alterne entre itens vizinhos para o conjunto
 * lembrar um espectro se abrindo.
 */
export function ItemAnimado({
  children,
  origem = 'esquerda',
  className = '',
}: {
  children: ReactNode
  origem?: 'esquerda' | 'direita'
  className?: string
}) {
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
