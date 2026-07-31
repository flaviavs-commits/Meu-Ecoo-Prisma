import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { ItemAnimado, ListaAnimada } from '../ui/Animar'
import { Secao, TituloSecao } from '../ui/Secao'
import { planos } from '../../content/landing'
import { ENTRADA_APP } from '../../content/destinos'

/** Planos de tokens do aluno individual, à parte do plano institucional. */
export function Planos() {
  return (
    <Secao id="planos" fundo="branco">
      <TituloSecao
        etiqueta={planos.etiqueta}
        titulo={planos.titulo}
        descricao={planos.descricao}
        clima="neutro"
      />
      <p className="mt-3 max-w-xl text-sm text-texto-secundario">{planos.baseComum}</p>

      <ListaAnimada className="mt-12 grid items-start gap-6 md:grid-cols-3">
        {planos.itens.map((plano) => (
          <ItemAnimado key={plano.id}>
            <Card
              interativo
              brilho={
                plano.destaque === 'premium'
                  ? 'rgb(123 120 200 / 0.55)'
                  : plano.destaque === 'recomendado'
                    ? 'rgb(123 120 200 / 0.35)'
                    : undefined
              }
              className={[
                'relative flex h-full flex-col p-9 sm:p-10',
                /*
                  Progressão de contorno pelos 3 planos, do mais sutil ao
                  mais forte - fundo continua claro em todos, só a borda
                  escurece e engrossa. Recomendado (Pro) e Premium (Ultra)
                  ganham também sombra e selo, na mesma lógica de antes.
                */
                plano.destaque === null
                  ? 'border-contorno-forte'
                  : plano.destaque === 'recomendado'
                    ? 'border-texto shadow-[0_12px_32px_-16px_rgb(26_26_26/0.35)]'
                    : 'border-2 border-texto shadow-[0_16px_40px_-16px_rgb(26_26_26/0.45)]',
              ].join(' ')}
            >
              {plano.destaque === 'premium' && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-texto px-3.5 py-1 text-[11px] font-medium tracking-[0.1em] text-superficie uppercase">
                  Mais completo
                </span>
              )}

              <p className="text-xs font-medium tracking-[0.12em] text-texto-secundario uppercase">
                {plano.nome}
              </p>
              <p className="mt-2 text-sm text-texto-secundario">{plano.resumo}</p>

              <p className="fonte-display mt-8 text-4xl whitespace-nowrap">
                {plano.preco}
                <span className="text-lg text-texto-secundario">{plano.periodo}</span>
              </p>

              {/* Limite de uso: métrica principal do plano, isolada dos demais benefícios */}
              <p className="mt-5 rounded-md bg-superficie-alt px-3.5 py-2.5 text-sm font-medium">
                {plano.itens[0]}
              </p>

              <ul className="mt-6 flex-1 space-y-4.5">
                {plano.itens.slice(1).map((item) => (
                  <li key={item} className="flex gap-3 text-sm">
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 20 20"
                      fill="none"
                      aria-hidden="true"
                      className="mt-0.5 shrink-0 text-texto"
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

              <Button
                href={ENTRADA_APP}
                variant={plano.destaque !== null ? 'primary' : 'secondary'}
                className="mt-10 w-full"
              >
                Escolher {plano.nome}
              </Button>
            </Card>
          </ItemAnimado>
        ))}
      </ListaAnimada>
    </Secao>
  )
}
