import { Card } from '../ui/Card'
import { Card3D } from '../ui/Card3D'
import { ItemAnimado, ListaAnimada } from '../ui/Animar'
import { Secao, TituloSecao } from '../ui/Secao'
import { perfis } from '../../content/landing'

/** Três caminhos de uso: aluno, professor e diretor. */
export function Perfis() {
  return (
    <Secao id="perfis">
      <TituloSecao
        etiqueta="Perfis"
        titulo="Um caminho para cada perfil"
        clima="neutro"
      />

      <ListaAnimada className="mt-12 grid gap-6 md:grid-cols-3">
        {perfis.map((perfil, indice) => (
          /* Lados alternados: o trio se abre como um espectro */
          <ItemAnimado
            key={perfil.id}
            origem={indice % 2 === 0 ? 'esquerda' : 'direita'}
          >
            <Card3D brilho={perfil.corVar} className="h-full">
              <Card interativo className="flex h-full flex-col overflow-hidden p-0!">
                {/* Cabeçalho tingido: superfície do perfil, com faixa cheia acima */}
                <span
                  aria-hidden="true"
                  className="block h-1.5 w-full"
                  style={{ backgroundColor: perfil.corVar }}
                />

                <div
                  className="flex flex-1 flex-col p-7"
                  style={{ backgroundColor: perfil.tintVar }}
                >
                  <h3 className="text-xl">{perfil.nome}</h3>
                  <p className="mt-1.5 text-sm text-texto-secundario">
                    {perfil.foco}
                  </p>

                  <ul className="mt-6 space-y-3.5">
                    {perfil.itens.map((item) => (
                      <li key={item} className="flex gap-3 text-sm">
                        <svg
                          width="18"
                          height="18"
                          viewBox="0 0 20 20"
                          fill="none"
                          aria-hidden="true"
                          className="mt-0.5 shrink-0"
                          style={{ color: perfil.corVar }}
                        >
                          <path
                            d="M4 10.5l4 4 8-8.5"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                        <span className="text-texto-secundario">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>
            </Card3D>
          </ItemAnimado>
        ))}
      </ListaAnimada>
    </Secao>
  )
}
