import { motion, useReducedMotion } from 'motion/react'
import { Button } from '../ui/Button'
import { Titulo3D } from '../ui/Titulo3D'
import { hero } from '../../content/landing'
import { SUAVE } from '../ui/movimento'

/**
 * Primeira dobra, em tela cheia.
 *
 * DUAS DECISÕES DE ESTRUTURA:
 *
 * 1. ALTURA MÍNIMA DE VIEWPORT (min-h-svh). Sem isso a seção tem só
 *    a altura do conteúdo, e a cor da PRÓXIMA seção invade o campo
 *    de visão - o defeito que aparecia antes. Usa `svh` e não `vh`
 *    porque no celular a barra do navegador some e volta; `vh` fixo
 *    causa salto de layout, `svh` acompanha.
 *
 * 2. TÍTULO EM DUAS ESCALAS. "Uma entrada." fica pequeno e discreto;
 *    "Todo o espectro do ensino." domina. Uma frase inteira no mesmo
 *    corpo vira parede de texto em caixa alta - o contraste de
 *    tamanho é o que cria hierarquia e impacto ao mesmo tempo.
 */
export function Hero() {
  const reduzido = useReducedMotion()

  const bloco = (atraso: number) =>
    reduzido
      ? {}
      : {
          initial: { opacity: 0, y: 14 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.7, delay: atraso, ease: SUAVE },
        }

  return (
    <section
      id="inicio"
      className="relative flex min-h-svh flex-col justify-center overflow-hidden border-b border-contorno bg-superficie-alt px-4 py-20 sm:px-10 sm:py-24"
    >
      <div className="mx-auto w-full max-w-6xl">
        {/* Marcador de capítulo: ancora a composição à esquerda */}
        <motion.div
          className="flex items-center gap-4 text-texto-secundario"
          {...bloco(0)}
        >
          <span className="h-px w-12 bg-contorno-forte" />
          <span className="text-xs tracking-[0.16em] uppercase">
            {hero.etiqueta}
          </span>
        </motion.div>

        {/* Título em duas escalas, alinhado à esquerda */}
        <h1 className="mt-10 max-w-5xl">
          <span className="fonte-display block text-2xl text-texto-secundario sm:text-3xl">
            <Titulo3D texto="Uma entrada." clima="professor" />
          </span>
          <span className="fonte-display mt-3 block text-5xl leading-[0.95] sm:text-7xl lg:text-8xl">
            <Titulo3D texto="Todo o espectro do ensino." clima="neutro" />
          </span>
        </h1>

        <motion.p
          className="mt-10 max-w-xl text-lg leading-relaxed text-texto-secundario text-pretty sm:text-xl"
          {...bloco(0.55)}
        >
          {hero.subtitulo}
        </motion.p>

        <motion.div
          className="mt-10 flex flex-col gap-3 sm:mt-12 sm:flex-row"
          {...bloco(0.68)}
        >
          <Button className="w-full sm:w-auto" size="lg" href="#comecar">
            {hero.ctaPrimario}
          </Button>
          <Button className="w-full sm:w-auto" size="lg" variant="secondary" href="#como-funciona">
            {hero.ctaSecundario}
          </Button>
        </motion.div>

        <motion.p
          className="mt-6 text-sm text-texto-secundario"
          {...bloco(0.78)}
        >
          {hero.apoio}
        </motion.p>
      </div>

      {/* Indicador de rolagem, ancorado ao rodapé da dobra */}
      {!reduzido && (
        <motion.div
          aria-hidden="true"
          className="absolute inset-x-0 bottom-8 flex justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4, duration: 0.8 }}
        >
          <motion.span
            className="h-10 w-px bg-contorno-forte"
            animate={{ scaleY: [0.3, 1, 0.3], originY: 0 }}
            transition={{ duration: 2.4, repeat: Infinity, ease: 'easeInOut' }}
          />
        </motion.div>
      )}
    </section>
  )
}
