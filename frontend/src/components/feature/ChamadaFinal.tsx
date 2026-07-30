import { Button } from '../ui/Button'
import { AoEntrar } from '../ui/Animar'
import { ctaFinal } from '../../content/landing'
import { ENTRADA_APP } from '../../content/destinos'

/** Última conversão antes do rodapé. */
export function ChamadaFinal() {
  return (
    <section id="comecar" className="px-6 py-20 sm:py-24">
      {/* Bloco de destaque em rose, com borda marcada e faixa espectral */}
      <AoEntrar className="relative mx-auto max-w-5xl overflow-hidden rounded-lg border border-contorno bg-terracotta-tint px-6 py-20 text-center sm:px-12 sm:py-24">
        <div aria-hidden="true" className="absolute inset-x-0 top-0 flex h-1.5">
          <span className="flex-1 bg-aluno" />
          <span className="flex-1 bg-professor" />
          <span className="flex-1 bg-diretor" />
        </div>

        <h2 className="fonte-display text-3xl text-balance sm:text-5xl">
          {ctaFinal.titulo}
        </h2>
        <p className="mx-auto mt-6 max-w-lg text-lg leading-relaxed text-texto-secundario text-pretty">
          {ctaFinal.descricao}
        </p>

        <div className="mt-10 flex justify-center">
          {/* Mesma porta do "Entrar" no header: a tela inicial da aplicacao */}
          <Button size="lg" href={ENTRADA_APP}>
            {ctaFinal.botao}
          </Button>
        </div>

        <p className="mt-6 text-sm text-texto-secundario">{ctaFinal.apoio}</p>
      </AoEntrar>
    </section>
  )
}
