import type { ReactNode } from 'react'
import { useRef } from 'react'
import { Atmosfera } from './Atmosfera'
import { Portal } from './Portal'
import type { Clima } from './clima'

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
        'relative flex min-h-svh flex-col justify-center overflow-hidden [content-visibility:auto] [contain-intrinsic-size:auto_900px]',
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
