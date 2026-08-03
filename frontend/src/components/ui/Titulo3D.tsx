import { memo, useMemo } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import type { Clima } from './clima'
import { ASSENTA } from './movimento'

/**
 * Título com entrada tridimensional e refração cromática.
 *
 * NOTAS DE DESEMPENHO - por que este componente é assim:
 *
 * A versão anterior desenhava cada letra QUATRO vezes (três cópias
 * coloridas com `mix-blend-screen` + a letra real). Num título de 40
 * letras isso são 160 nós, cada um forçando o compositor a refazer
 * a mistura a cada quadro - e travava.
 *
 * Aqui a refração vem de `text-shadow` com três sombras coloridas:
 * um único nó por letra, resolvido na pintura, sem camada de
 * composição extra. O efeito visual é praticamente o mesmo e o
 * custo cai por volta de quatro vezes.
 *
 * As demais regras: só `opacity`, `transform` e `filter` são
 * animados - as três propriedades que a GPU acelera. Nada de animar
 * `width`, `top` ou cor.
 */

/**
 * Deslocamento inicial por clima. Valores contidos de propósito:
 * distâncias grandes exigem áreas de pintura maiores e pioram o
 * custo sem melhorar a leitura do movimento.
 */
const porClima: Record<
  Clima,
  (i: number, total: number) => { x: number; y: number; z: number; rot: number }
> = {
  aluno: (i) => ({
    x: (i % 3 === 0 ? -1 : 1) * (8 + (i % 4) * 4),
    y: -46 - (i % 3) * 12,
    z: -180 - (i % 3) * 60,
    rot: (i % 2 === 0 ? -1 : 1) * 14,
  }),
  professor: (i, total) => {
    const esquerda = i < total / 2
    return {
      x: (esquerda ? -1 : 1) * (58 + (i % 3) * 14),
      y: (i % 2 === 0 ? -1 : 1) * 12,
      z: -150 - (i % 3) * 50,
      rot: (esquerda ? -1 : 1) * 16,
    }
  },
  diretor: (i, total) => ({
    x: (i - total / 2) * 6,
    y: 50 + (i % 3) * 12,
    z: -140 - (i % 4) * 40,
    rot: (i - total / 2) * 2,
  }),
  neutro: (i, total) => {
    const centro = i - total / 2
    return {
      x: centro * 10,
      y: (i % 2 === 0 ? -1 : 1) * 28,
      z: -220 - Math.abs(centro) * 26,
      rot: centro * 2.5,
    }
  },
}

/**
 * Refração em três sombras. No estado inicial elas estão separadas
 * (luz decomposta); no final convergem a zero (luz recomposta).
 */
const SOMBRA_SEPARADA =
  '-4px -2px 0 var(--color-lavender), 4px 2px 0 var(--color-terracotta), 1px 3px 0 var(--color-olive)'
const SOMBRA_UNIDA =
  '0 0 0 transparent, 0 0 0 transparent, 0 0 0 transparent'

interface Titulo3DProps {
  texto: string
  clima?: Clima
  className?: string
}

export const Titulo3D = memo(function Titulo3D({
  texto,
  clima = 'neutro',
  className = '',
}: Titulo3DProps) {
  const reduzido = useReducedMotion()

  const palavras = useMemo(() => {
    let n = 0
    return texto.split(' ').map((palavra) => ({
      palavra,
      letras: [...palavra].map((letra) => ({ letra, indice: n++ })),
    }))
  }, [texto])

  const total = useMemo(
    () => [...texto].filter((c) => c !== ' ').length,
    [texto],
  )

  if (reduzido) {
    return <span className={className}>{texto}</span>
  }

  const origem = porClima[clima]

  return (
    <motion.span
      className={['inline-block', className].join(' ')}
      aria-label={texto}
      initial="oculto"
      whileInView="visivel"
      viewport={{ once: true, margin: '-90px' }}
      variants={{ visivel: { transition: { staggerChildren: 0.05 } } }}
      style={{ perspective: 700 }}
    >
      {palavras.map(({ palavra, letras }, ip) => (
        <span
          key={`${palavra}-${ip}`}
          aria-hidden="true"
          className="inline-block whitespace-nowrap"
        >
          {letras.map(({ letra, indice }) => {
            const de = origem(indice, total)
            return (
              <motion.span
                key={indice}
                className="inline-block"
                variants={{
                  oculto: {
                    opacity: 0,
                    x: de.x,
                    y: de.y,
                    z: de.z,
                    rotateX: de.rot,
                    textShadow: SOMBRA_SEPARADA,
                  },
                  visivel: {
                    opacity: 1,
                    x: 0,
                    y: 0,
                    z: 0,
                    rotateX: 0,
                    textShadow: SOMBRA_UNIDA,
                  },
                }}
                transition={{ duration: 1.1, ease: ASSENTA }}
              >
                {letra}
              </motion.span>
            )
          })}
          {ip < palavras.length - 1 && (
            <span className="inline-block">&nbsp;</span>
          )}
        </span>
      ))}
    </motion.span>
  )
})
