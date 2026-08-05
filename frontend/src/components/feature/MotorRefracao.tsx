import { useEffect, useRef, useState } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { Secao } from '../ui/Secao'
import { TituloSecao } from '../ui/TituloSecao'
import { exemplosRefracao } from '../../mocks/exemplosRefracao'
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

const perfisDemo = [
  { id: 'aluno', rotulo: 'Ver como aluno', cor: 'var(--color-aluno)', tint: 'bg-aluno-tint' },
  { id: 'professor', rotulo: 'Ver como professor', cor: 'var(--color-professor)', tint: 'bg-professor-tint' },
  { id: 'diretor', rotulo: 'Ver como diretor', cor: 'var(--color-diretor)', tint: 'bg-diretor-tint' },
] as const

/**
 * Demo estático do motor: um tema entra, três materiais saem.
 * Ilustrativo - não chama o backend ainda. A integração real
 * entra na Fase 1, junto com o gateway de IA.
 */
export function MotorRefracao() {
  const [ativo, setAtivo] = useState(0)
  const [perfilAtivo, setPerfilAtivo] = useState<(typeof perfisDemo)[number]['id']>('aluno')
  const [menuAberto, setMenuAberto] = useState(false)
  const seletorRef = useRef<HTMLDivElement>(null)
  const gatilhoRef = useRef<HTMLButtonElement>(null)
  const exemplo = exemplosRefracao[ativo]
  const saidasVisiveis = exemplo.saidas.filter((saida) => saida.perfil === perfilAtivo)
  const reduzido = useReducedMotion()

  useEffect(() => {
    function fecharAoClicarFora(event: MouseEvent) {
      if (!seletorRef.current?.contains(event.target as Node)) setMenuAberto(false)
    }

    document.addEventListener('mousedown', fecharAoClicarFora)
    return () => document.removeEventListener('mousedown', fecharAoClicarFora)
  }, [])

  return (
    <Secao id="como-funciona" fundo="aluno">
      <TituloSecao
        etiqueta="Como funciona"
        titulo="Um tema entra. Materiais prontos saem."
        descricao="Veja o que cada perfil pode fazer com o mesmo tema."
        clima="aluno"
      />

      <div
        className="mt-8 inline-flex flex-wrap gap-1 rounded-full border border-contorno bg-superficie p-1"
        role="group"
        aria-label="Visualizar materiais por perfil"
      >
        {perfisDemo.map((perfil) => {
          const selecionado = perfil.id === perfilAtivo
          return (
            <button
              key={perfil.id}
              type="button"
              aria-pressed={selecionado}
              onClick={() => setPerfilAtivo(perfil.id)}
              className={[
                'flex min-h-9 items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium transition-colors duration-200',
                selecionado
                  ? `${perfil.tint} text-texto shadow-[0_2px_10px_-6px_rgb(26_26_26/0.4)]`
                  : 'text-texto-secundario hover:bg-fundo hover:text-texto',
              ].join(' ')}
            >
              <span
                aria-hidden="true"
                className="h-2 w-2 shrink-0 rounded-full"
                style={{ backgroundColor: perfil.cor }}
              />
              {perfil.rotulo}
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
            <div
              ref={seletorRef}
              className="relative mt-3 max-w-xl"
              onKeyDown={(event) => {
                if (event.key !== 'Escape') return
                setMenuAberto(false)
                gatilhoRef.current?.focus()
              }}
            >
              <button
                ref={gatilhoRef}
                type="button"
                aria-haspopup="listbox"
                aria-expanded={menuAberto}
                aria-label="Selecionar matéria"
                onClick={() => setMenuAberto((aberto) => !aberto)}
                onKeyDown={(event) => {
                  if (event.key === 'ArrowDown') {
                    event.preventDefault()
                    setMenuAberto(true)
                    setAtivo((valor) => (valor + 1) % exemplosRefracao.length)
                  }
                  if (event.key === 'ArrowUp') {
                    event.preventDefault()
                    setMenuAberto(true)
                    setAtivo((valor) => (valor - 1 + exemplosRefracao.length) % exemplosRefracao.length)
                  }
                }}
                className="group flex w-full items-center justify-between gap-4 border-b border-contorno border-b-aluno bg-transparent px-0 pb-3 pt-1 text-left outline-none transition-all hover:border-b-texto focus:border-b-texto focus:ring-0"
              >
                <span className="flex min-w-0 items-center gap-3">
                  <span
                    aria-hidden="true"
                    className="h-2 w-2 shrink-0 rounded-full bg-aluno"
                  >
                  </span>
                  <span className="min-w-0">
                    <span className="block text-[10px] font-medium tracking-[0.16em] text-texto-secundario uppercase">
                      Tema selecionado
                    </span>
                    <span className="fonte-display mt-0.5 block truncate text-xl font-bold tracking-[0.04em] uppercase sm:text-2xl">
                      {exemplo.entrada}
                    </span>
                  </span>
                </span>
                <span
                  aria-hidden="true"
                  className={["flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-texto-secundario transition-all duration-200 group-hover:bg-texto/5 group-hover:text-texto", menuAberto ? "rotate-180 bg-texto/5 text-texto" : ""].join(' ')}
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="m3 5 4 4 4-4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
              </button>

              {menuAberto && (
                <div
                  role="listbox"
                  aria-label="Matérias disponíveis"
                  className="absolute z-20 mt-3 w-full overflow-hidden rounded-xl border border-contorno bg-superficie/95 p-1.5 shadow-[0_18px_40px_-20px_rgb(26_26_26/0.55)] backdrop-blur-sm"
                >
                  {exemplosRefracao.map((item, indice) => {
                    const selecionado = indice === ativo
                    return (
                      <button
                        key={item.entrada}
                        type="button"
                        role="option"
                        aria-selected={selecionado}
                        onClick={() => {
                          setAtivo(indice)
                          setMenuAberto(false)
                        }}
                        className={[
                          'relative flex w-full items-center justify-between overflow-hidden rounded-lg px-3.5 py-3 text-left text-sm font-medium transition-colors',
                          selecionado
                            ? 'bg-texto text-fundo shadow-[0_8px_20px_-12px_rgb(26_26_26/0.65)]'
                            : 'text-texto-secundario hover:bg-fundo hover:text-texto',
                        ].join(' ')}
                      >
                        {selecionado && (
                          <span aria-hidden="true" className="absolute inset-x-0 top-0 flex h-1">
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
              )}
            </div>
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
                key="entrada"
              />

              {/* Espectro: os tres raios saem em sequencia, apos o feixe */}
              {raiosEspectro.map((raio, indice) => (
                <motion.path
                  key={raio.d}
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
              {saidasVisiveis.map((saida, indice) => {
                const destino = porPerfil[saida.perfil]
                return (
                  <motion.li
                    /* key com `ativo` refaz a entrada a cada troca de exemplo */
                    key={`${ativo}-${saida.rotulo}`}
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
            {saidasVisiveis.length === 0 && (
              <p className="mt-3 rounded-md border border-dashed border-contorno px-4 py-4 text-sm text-texto-secundario">
                Nenhum material de demonstração para este perfil neste tema.
              </p>
            )}
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
