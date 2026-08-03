import { Card } from '../ui/Card'
import { Card3D } from '../ui/Card3D'
import { ItemAnimado } from '../ui/ItemAnimado'
import { ListaAnimada } from '../ui/ListaAnimada'
import { Secao } from '../ui/Secao'
import { TituloSecao } from '../ui/TituloSecao'
import { recursos } from '../../content/landing'

/**
 * Tons do filete e do glow, ciclados pelos cards.
 * O documento de identidade pede brilho no tom correspondente ao
 * card no hover; o valor "suave" é o mesmo tom com alfa, para o
 * anel não competir com o contorno preto.
 */
const tonsGlow = [
  { cheio: 'var(--color-terracotta)', suave: 'rgb(200 90 60 / 0.35)' },
  { cheio: 'var(--color-olive)', suave: 'rgb(106 133 80 / 0.35)' },
  { cheio: 'var(--color-lavender)', suave: 'rgb(123 120 200 / 0.35)' },
]

/** Grid de capacidades da plataforma. */
export function Recursos() {
  return (
    <Secao id="recursos" fundo="diretor">
      <TituloSecao
        etiqueta="Recursos"
        titulo="O que sustenta a plataforma"
        clima="diretor"
      />

      <ListaAnimada className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {recursos.map((recurso, indice) => {
          // Doc: glow no tom correspondente ao passar o mouse
          const tom = tonsGlow[indice % tonsGlow.length]
          return (
            <ItemAnimado
              key={recurso.titulo}
              origem={indice % 2 === 0 ? 'esquerda' : 'direita'}
            >
              <Card3D brilho={tom.cheio} className="h-full">
                <Card interativo brilho={tom.suave} className="h-full">
                  <span
                    aria-hidden="true"
                    className="block h-1 w-10 rounded-full"
                    style={{ backgroundColor: tom.cheio }}
                  />
                  <h3 className="mt-5 text-lg">{recurso.titulo}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-texto-secundario">
                    {recurso.descricao}
                  </p>
                </Card>
              </Card3D>
            </ItemAnimado>
          )
        })}
      </ListaAnimada>
    </Secao>
  )
}
