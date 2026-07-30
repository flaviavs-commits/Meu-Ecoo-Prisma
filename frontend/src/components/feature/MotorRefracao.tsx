import { useState } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { Secao, TituloSecao } from '../ui/Secao'
import { exemplosRefracao } from '../../content/landing'
import { SUAVE } from '../ui/movimento'

/**
 * Os três raios que saem do prisma, um por perfil.
 * Nascem no meio da face direita do triângulo (92,54) e se abrem em
 * leque bem espaçado, para as três cores ficarem legíveis a esta
 * escala - juntos demais, viravam um borrão indistinguível.
 */
const raiosEspectro = [
  { d: 'M92 35 128 18', cor: 'var(--color-aluno)' },
  { d: 'M92 49h38', cor: 'var(--color-professor)' },
  { d: 'M92 63 128 80', cor: 'var(--color-diretor)' },
]

/**
 * Cor e rótulo por perfil destinatário. A cor identifica PARA QUEM a
 * saida serve, não a ordem em que aparece.
 */
const porPerfil = {
  aluno: { cor: 'var(--color-aluno)', rotulo: 'Aluno' },
  professor: { cor: 'var(--color-professor)', rotulo: 'Professor' },
  diretor: { cor: 'var(--color-diretor)', rotulo: 'Diretor' },
} as const

/**
 * Demo estático do motor: um tema entra, três materiais saem.
 * Ilustrativo - não chama o backend ainda. A integração real
 * entra na Fase 1, junto com o gateway de IA.
 */
export function MotorRefracao() {
  const [ativo, setAtivo] = useState(0)
  const exemplo = exemplosRefracao[ativo]
  const reduzido = useReducedMotion()

  return (
    <Secao id="como-funciona" fundo="aluno">
      <TituloSecao
        etiqueta="Como funciona"
        titulo="Um tema entra. Materiais prontos saem."
        descricao="Escolha um exemplo."
        clima="aluno"
      />

      <div className="mt-12 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {exemplosRefracao.map((item, indice) => {
          const selecionado = indice === ativo
          return (
            <button
              key={item.entrada}
              type="button"
              aria-pressed={selecionado}
              onClick={() => setAtivo(indice)}
              className={[
                'relative rounded-lg border p-4 text-left text-sm transition-all duration-200',
                selecionado
                  /*
                    A aba ativa inverte contra o fundo da secao: usa a
                    cor do texto como preenchimento e o fundo da secao
                    como tinta. Assim funciona no creme e no breu sem
                    precisar de variante por tema. O filete espectral
                    no topo reforca que esta e a entrada "ativa" do prisma.
                  */
                  ? 'border-texto bg-texto text-fundo shadow-[0_8px_24px_-12px_rgb(26_26_26/0.5)]'
                  : 'border-contorno bg-superficie text-texto-secundario hover:-translate-y-0.5 hover:border-texto/50 hover:text-texto',
              ].join(' ')}
            >
              {selecionado && (
                <span
                  aria-hidden="true"
                  className="absolute inset-x-0 top-0 flex h-1 overflow-hidden rounded-t-lg"
                >
                  <span className="flex-1 bg-aluno" />
                  <span className="flex-1 bg-professor" />
                  <span className="flex-1 bg-diretor" />
                </span>
              )}
              {item.entrada}
            </button>
          )
        })}
      </div>

      <div className="mt-8 rounded-lg border border-contorno bg-superficie p-8 sm:p-12">
        <div className="grid items-center gap-10 lg:grid-cols-[1fr_auto_1.4fr]">
          {/* Entrada */}
          <div>
            <p className="text-xs font-medium tracking-[0.12em] text-texto-secundario uppercase">
              Entrada
            </p>
            <p className="fonte-display mt-3 text-2xl font-bold tracking-wide uppercase">
              {exemplo.entrada}
            </p>
          </div>

          {/* Prisma: feixe entra, triangulo refrata, espectro sai */}
          <div aria-hidden="true" className="hidden justify-center lg:flex">
            <svg width="152" height="108" viewBox="0 0 152 108" fill="none">
              {/* Glow suave atras do prisma: da peso ao elemento central */}
              <circle cx="56" cy="54" r="42" fill="url(#brilhoPrisma)" />

              <path
                d="M56 16 92 82H20L56 16Z"
                stroke="var(--color-texto)"
                strokeWidth="2.5"
                strokeLinejoin="round"
                fill="var(--color-superficie)"
              />

              {/* Feixe de entrada: risca ate o prisma */}
              <motion.path
                d="M0 54h18"
                stroke="var(--color-texto-secundario)"
                strokeWidth="2.5"
                strokeLinecap="round"
                initial={reduzido ? false : { pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.4, ease: SUAVE }}
                /* key faz a animacao repetir quando o exemplo muda */
                key={`entrada-${ativo}`}
              />

              {/* Espectro: os tres raios saem em sequencia, apos o feixe */}
              {raiosEspectro.map((raio, indice) => (
                <motion.path
                  key={`${raio.d}-${ativo}`}
                  d={raio.d}
                  stroke={raio.cor}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  initial={reduzido ? false : { pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{
                    duration: 0.45,
                    delay: 0.35 + indice * 0.12,
                    ease: SUAVE,
                  }}
                />
              ))}

              <defs>
                <radialGradient id="brilhoPrisma">
                  <stop offset="0%" stopColor="var(--color-lavender)" stopOpacity="0.16" />
                  <stop offset="100%" stopColor="var(--color-lavender)" stopOpacity="0" />
                </radialGradient>
              </defs>
            </svg>
          </div>

          {/* Saidas */}
          <div>
            <p className="text-xs font-medium tracking-[0.12em] text-texto-secundario uppercase">
              Saídas
            </p>
            <ul className="mt-3 space-y-2.5">
              {exemplo.saidas.map((saida, indice) => {
                const destino = porPerfil[saida.perfil]
                return (
                  <motion.li
                    /* key com `ativo` refaz a entrada a cada troca de exemplo */
                    key={`${saida.rotulo}-${ativo}`}
                    className="flex items-center justify-between gap-4 rounded-md border border-contorno bg-superficie px-4 py-4 transition-colors duration-200 hover:border-texto/40"
                    style={{ borderLeft: `3px solid ${destino.cor}` }}
                    initial={reduzido ? false : { opacity: 0, x: 12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{
                      duration: 0.4,
                      delay: reduzido ? 0 : 0.45 + indice * 0.1,
                      ease: SUAVE,
                    }}
                  >
                    <span className="text-sm font-medium">{saida.rotulo}</span>

                    {/*
                      A cor identifica o destinatário, mas o RÓTULO fica em
                      texto-secundario, não no acento: nenhum dos três tons
                      atinge 4.5:1 em texto pequeno (doc, "Acessibilidade &
                      Contraste"). A cor vive no marcador e na borda, que
                      são decorativos.
                    */}
                    <span className="flex shrink-0 items-center gap-2 text-xs text-texto-secundario">
                      <span
                        aria-hidden="true"
                        className="h-2.5 w-2.5 rounded-full border border-contorno"
                        style={{ backgroundColor: destino.cor }}
                      />
                      {destino.rotulo}
                    </span>
                  </motion.li>
                )
              })}
            </ul>
          </div>
        </div>

        <p className="mt-8 border-t border-borda pt-5 text-sm text-texto-secundario">
          Todo material gerado nasce como rascunho e passa pela revisão do professor
          antes de valer nota.
        </p>
      </div>
    </Secao>
  )
}
