import type { ReactNode, RefObject } from 'react'
import { motion, useReducedMotion, useScroll, useTransform } from 'motion/react'
import type { Clima } from './clima'

/**
 * Camadas atmosféricas de uma seção.
 *
 * NOTAS DE DESEMPENHO - por que só duas camadas:
 *
 * A versão anterior empilhava quatro (véu, duas auroras, vinheta e
 * grão). Cada `blur-3xl` cria uma camada de composição do tamanho do
 * elemento, e o grão em `mix-blend-overlay` obrigava o navegador a
 * recompor a seção inteira a cada quadro de rolagem. Somando as
 * seções, isso era a maior fonte de travamento da página.
 *
 * Ficaram duas camadas, ambas só com `opacity` e `transform`
 * animados - o que a GPU resolve sem repintar:
 *
 *   VÉU     tinge o ambiente com o tom do clima
 *   AURORA  um foco de luz que deriva devagar, dando profundidade
 *
 * A vinheta virou uma sombra interna estática (sem custo por quadro)
 * e o grão saiu: era o efeito mais caro e o menos percebido.
 */

export type { Clima } from './clima'

/** Tom principal de cada clima. */
const tons: Record<Clima, string> = {
  aluno: 'var(--color-aluno)',
  professor: 'var(--color-professor)',
  diretor: 'var(--color-diretor)',
  neutro: 'var(--color-terracotta)',
}

interface AtmosferaProps {
  /** Seção que serve de referência para o progresso de rolagem. */
  alvo: RefObject<HTMLElement | null>
  clima: Clima
}

export function Atmosfera({ alvo, clima }: AtmosferaProps) {
  const reduzido = useReducedMotion()

  const { scrollYProgress } = useScroll({
    target: alvo,
    offset: ['start end', 'end start'],
  })

  // Curva base: 0 fora da tela, 1 no auge (seção centrada).
  const auge = useTransform(scrollYProgress, [0, 0.34, 0.66, 1], [0, 1, 1, 0])

  const opacidadeVeu = useTransform(auge, [0, 1], [0, 0.16])
  const opacidadeAurora = useTransform(auge, [0, 1], [0, 0.2])

  // Deriva lenta e curta: sugere profundidade sem exigir repintura ampla.
  const auroraSobe = useTransform(scrollYProgress, [0, 1], ['8%', '-8%'])

  if (reduzido) return null

  const tom = tons[clima]

  return (
    <>
      {/* Véu cromático */}
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 z-0"
        style={{
          opacity: opacidadeVeu,
          background: `radial-gradient(120% 80% at 50% 0%, ${tom}, transparent 70%)`,
          willChange: 'opacity',
        }}
      />

      {/* Aurora: foco difuso em deriva lenta */}
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute -top-1/3 left-1/2 z-0 h-[60%] w-[80%] -translate-x-1/2 rounded-full blur-3xl"
        style={{
          opacity: opacidadeAurora,
          y: auroraSobe,
          background: `radial-gradient(circle, ${tom}, transparent 68%)`,
          willChange: 'transform, opacity',
        }}
      />
    </>
  )
}

interface PortalProps {
  children: ReactNode
  alvo: RefObject<HTMLElement | null>
  className?: string
}

/**
 * Emergência suave do conteúdo ao entrar na seção.
 *
 * NOTA DE DESEMPENHO: a versão anterior animava `mask-image` e
 * `filter: blur` por rolagem. Máscara em gradiente é das operações
 * mais caras que existem em CSS, e animá-la a cada quadro travava em
 * GPU modesta. Aqui restaram `opacity` e `scale` - baratas e
 * suficientes para a sensação de emergir.
 */
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
