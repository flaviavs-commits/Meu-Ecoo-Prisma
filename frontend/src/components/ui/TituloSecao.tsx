import type { Clima } from './clima'
import { ItemAnimado } from './ItemAnimado'
import { ListaAnimada } from './ListaAnimada'
import { Titulo3D } from './Titulo3D'

interface TituloSecaoProps {
  etiqueta?: string
  titulo: string
  descricao?: string
  numero?: string
  clima?: Clima
  className?: string
}

/** Cabeçalho de seção com etiqueta, título e descrição opcionais. */
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
