import { memo, type PointerEvent, type ReactNode } from 'react'
import { useRef } from 'react'
import {
  motion,
  useMotionValue,
  useReducedMotion,
  useSpring,
  useTransform,
} from 'motion/react'

/**
 * Invólucro que dá volume sutil a um card.
 *
 * NOTAS DE DESEMPENHO:
 *
 * A versão anterior remontava uma string de `radial-gradient` a cada
 * movimento do ponteiro (via useMotionTemplate). Trocar `background`
 * a cada quadro obriga o navegador a repintar a camada inteira - era
 * a segunda maior fonte de travamento.
 *
 * Aqui o reflexo é um gradiente FIXO, e só a sua posição muda por
 * `transform` - que a GPU resolve sem repintar. Mesmo resultado
 * visual, custo muito menor.
 *
 * A inclinação também foi reduzida: 9 graus era exagerado e obrigava
 * áreas de composição maiores. Com 4 graus o volume continua legível
 * e o movimento fica mais elegante.
 */

interface Card3DProps {
  children: ReactNode
  /** Cor do brilho especular. Use o tom do clima da seção. */
  brilho?: string
  /** Intensidade da inclinação em graus. */
  intensidade?: number
  className?: string
}

export const Card3D = memo(function Card3D({
  children,
  brilho = 'var(--color-terracotta)',
  intensidade = 4,
  className = '',
}: Card3DProps) {
  const reduzido = useReducedMotion()
  const caixa = useRef<HTMLDivElement>(null)

  // Posição do ponteiro normalizada em -0.5..0.5.
  const px = useMotionValue(0)
  const py = useMotionValue(0)

  // Mola suave: responde sem oscilar.
  const mx = useSpring(px, { stiffness: 90, damping: 24, mass: 0.6 })
  const my = useSpring(py, { stiffness: 90, damping: 24, mass: 0.6 })

  const girarY = useTransform(mx, [-0.5, 0.5], [-intensidade, intensidade])
  const girarX = useTransform(my, [-0.5, 0.5], [intensidade, -intensidade])

  // O reflexo desliza por transform, não por recálculo de gradiente.
  const luzX = useTransform(mx, [-0.5, 0.5], ['-22%', '22%'])
  const luzY = useTransform(my, [-0.5, 0.5], ['-22%', '22%'])

  if (reduzido) {
    return <div className={className}>{children}</div>
  }

  const aoMover = (evento: PointerEvent<HTMLDivElement>) => {
    // Ignora toque: em tela sensível o "hover" gruda e piora a rolagem.
    if (evento.pointerType !== 'mouse') return
    const atual = caixa.current
    if (!atual) return
    const r = atual.getBoundingClientRect()
    px.set((evento.clientX - r.left) / r.width - 0.5)
    py.set((evento.clientY - r.top) / r.height - 0.5)
  }

  const aoSair = () => {
    px.set(0)
    py.set(0)
  }

  return (
    <motion.div
      ref={caixa}
      onPointerMove={aoMover}
      onPointerLeave={aoSair}
      className={['group relative', className].join(' ')}
      style={{
        perspective: 900,
        rotateX: girarX,
        rotateY: girarY,
        // Promove a camada uma vez, em vez de a cada quadro.
        willChange: 'transform',
      }}
    >
      {/* Reflexo especular: gradiente fixo, posição por transform */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 z-20 overflow-hidden rounded-lg opacity-0 transition-opacity duration-500 group-hover:opacity-100"
      >
        <motion.div
          className="absolute inset-[-30%]"
          style={{
            x: luzX,
            y: luzY,
            background: `radial-gradient(circle at 50% 50%, ${brilho}, transparent 55%)`,
            opacity: 0.16,
          }}
        />
      </div>

      {children}
    </motion.div>
  )
})
