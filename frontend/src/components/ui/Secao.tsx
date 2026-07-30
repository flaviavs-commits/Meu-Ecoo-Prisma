import type { ReactNode } from 'react'
import { useRef } from 'react'
import { ItemAnimado, ListaAnimada } from './Animar'
import { Atmosfera, Portal } from './Atmosfera'
import type { Clima } from './clima'
import { Titulo3D } from './Titulo3D'

/**
 * Fundo da seção.
 *
 * Os tons -tint são superfície, não significado (regra 2 em index.css):
 * dão cor a seção inteira sem competir com o acento cheio, que fica
 * reservado para identificar perfil de usuário.
 *
 * Prefira o tint que combina com o conteúdo da seção - falando de
 * aluno, use 'aluno'. Alterne com 'creme' para não empilhar duas
 * seções coloridas seguidas.
 */
type Fundo = 'creme' | 'branco' | 'aluno' | 'professor' | 'diretor'

interface SecaoProps {
  id?: string
  children: ReactNode
  /** Alterne entre seções vizinhas para criar ritmo. */
  fundo?: Fundo
  className?: string
}

const porFundo: Record<Fundo, string> = {
  creme: 'bg-fundo',
  branco: 'bg-superficie',
  aluno: 'bg-lavender-tint',
  professor: 'bg-terracotta-tint',
  diretor: 'bg-olive-tint',
}

/** Fundos neutros não recebem atmosfera: não há tom para projetar. */
const climaPorFundo: Record<Fundo, Clima | null> = {
  creme: null,
  branco: null,
  aluno: 'aluno',
  professor: 'professor',
  diretor: 'diretor',
}

/**
 * Container de seção, em tela cheia.
 *
 * ALTURA MÍNIMA DE VIEWPORT (min-h-svh): cada seção ocupa a tela
 * inteira, então a cor da seção seguinte nunca aparece por baixo do
 * conteúdo. Era o defeito visível antes - seções curtas deixavam
 * vazar o fundo da próxima. `svh` em vez de `vh` porque no celular a
 * barra do navegador aparece e some; `vh` fixo provoca salto.
 *
 * O conteúdo fica centrado verticalmente, o que dá a cada seção o
 * peso de um capítulo em vez de um bloco empilhado.
 */
export function Secao({
  id,
  children,
  fundo = 'creme',
  className = '',
}: SecaoProps) {
  const referencia = useRef<HTMLElement>(null)
  const clima = climaPorFundo[fundo]

  return (
    <section
      ref={referencia}
      id={id}
      className={[
        'relative flex min-h-svh flex-col justify-center overflow-hidden',
        'border-b border-contorno px-6 py-24 sm:px-10',
        porFundo[fundo],
        className,
      ].join(' ')}
    >
      {clima && <Atmosfera alvo={referencia} clima={clima} />}

      {clima ? (
        <Portal
          alvo={referencia}
          className="relative z-10 mx-auto w-full max-w-6xl"
        >
          {children}
        </Portal>
      ) : (
        <div className="relative z-10 mx-auto w-full max-w-6xl">{children}</div>
      )}
    </section>
  )
}

interface TituloSecaoProps {
  etiqueta?: string
  titulo: string
  descricao?: string
  /** Número do capítulo, exibido na régua lateral (ex.: "01"). */
  numero?: string
  /** Coreografia de entrada das letras. Use o mesmo tom do fundo. */
  clima?: Clima
  className?: string
}

/**
 * Cabeçalho de seção, em composição assimétrica.
 *
 * A régua com número de capítulo ancora o bloco à esquerda e o
 * título fica desalinhado do centro da página. É o que tira o
 * aspecto genérico de "tudo centralizado" - a leitura passa a ter
 * uma direção, em vez de um eixo de simetria.
 *
 * O título se monta letra a letra com o padrão do `clima` da seção,
 * então cada área da página tem sua própria coreografia de entrada.
 */
export function TituloSecao({
  etiqueta,
  titulo,
  descricao,
  numero,
  clima = 'neutro',
  className = '',
}: TituloSecaoProps) {
  return (
    <div className={['w-full', className].join(' ')}>
      {/* Régua de capítulo: número, filete e etiqueta na mesma linha */}
      {(numero || etiqueta) && (
        <ListaAnimada intervalo={0.1}>
          <ItemAnimado>
            <div className="flex items-center gap-4 text-texto-secundario">
              {numero && (
                <span className="fonte-display text-sm font-bold tracking-[0.2em]">
                  {numero}
                </span>
              )}
              <span className="h-px w-12 bg-contorno-forte" />
              {etiqueta && (
                <span className="text-xs tracking-[0.16em] uppercase">
                  {etiqueta}
                </span>
              )}
            </div>
          </ItemAnimado>
        </ListaAnimada>
      )}

      <h2 className="fonte-display mt-8 max-w-4xl text-4xl leading-[1.05] text-balance sm:text-6xl">
        <Titulo3D texto={titulo} clima={clima} />
      </h2>

      {descricao && (
        <ListaAnimada intervalo={0.1}>
          <ItemAnimado>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-texto-secundario text-pretty">
              {descricao}
            </p>
          </ItemAnimado>
        </ListaAnimada>
      )}
    </div>
  )
}
