import { memo, type CSSProperties, type ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  /** Realce sutil no hover. Use em cards clicaveis ou de destaque. */
  interativo?: boolean
  /**
   * Cor do brilho no hover, como valor CSS. O documento de identidade
   * pede glow no tom correspondente ao card (terracota, oliva ou lavanda).
   * Sem isso, o hover apenas escurece o contorno.
   */
  brilho?: string
  /**
   * Cor de fundo, como valor CSS. Use para destacar um card dentro
   * de um grupo - passar `style` de fora não funciona, porque o
   * atributo é reservado ao token de brilho.
   */
  fundo?: string
  className?: string
}

/** Superfície base para conteúdo agrupado. */
export const Card = memo(function Card({
  children,
  interativo = false,
  brilho,
  fundo,
  className = '',
}: CardProps) {
  const variaveis: CSSProperties = {}
  if (brilho) (variaveis as Record<string, string>)['--brilho'] = brilho
  if (fundo) variaveis.backgroundColor = fundo

  return (
    <div
      style={brilho || fundo ? variaveis : undefined}
      className={[
        // Contorno nítido e sem sombra difusa (doc), porém em grafite
        // suavizado - preto sólido ficou pesado demais na tela.
        // `bg-superficie` só se não houver fundo explícito.
        'rounded-lg border border-contorno p-7',
        fundo ? '' : 'bg-superficie',
        interativo ? 'transition-shadow duration-200' : '',
        interativo && brilho
          ? 'hover:shadow-[0_0_0_3px_var(--brilho)]'
          : '',
        className,
      ].join(' ')}
    >
      {children}
    </div>
  )
})
