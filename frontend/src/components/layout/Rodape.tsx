import { LogoComNome } from '../ui/Logo'
import { contatos, marca, rodape } from '../../content/landing'

/** Rodape com navegacao em colunas. */
export function Rodape() {
  const ano = new Date().getFullYear()

  return (
    <footer className="relative border-t border-contorno-forte bg-superficie-alt px-6 py-16">
      {/* Mesma faixa espectral do hero: abre e fecha a pagina */}
      <div aria-hidden="true" className="absolute inset-x-0 top-0 flex h-1">
        <span className="flex-1 bg-aluno" />
        <span className="flex-1 bg-professor" />
        <span className="flex-1 bg-diretor" />
      </div>

      <div className="mx-auto max-w-6xl">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div className="lg:col-span-1">
            <LogoComNome />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-texto-secundario">
              {marca.descricao}
            </p>

            {/* Contatos em botao circular */}
            <ul className="mt-6 flex gap-3">
              {contatos.map((contato) => (
                <li key={contato.rotulo}>
                  <a
                    href={contato.href}
                    aria-label={contato.rotulo}
                    className="flex h-11 w-11 items-center justify-center rounded-full border border-texto/25 text-texto transition-colors hover:border-marca hover:text-marca"
                  >
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <path
                        d={contato.icone}
                        stroke="currentColor"
                        strokeWidth="1.7"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {rodape.colunas.map((coluna) => (
            <nav key={coluna.titulo} aria-label={coluna.titulo}>
              <h2 className="text-xs font-medium tracking-[0.12em] text-texto uppercase">
                {coluna.titulo}
              </h2>
              <ul className="mt-4 space-y-2.5">
                {coluna.links.map((link) => (
                  <li key={link.rotulo}>
                    <a
                      href={link.href}
                      className="text-sm text-texto-secundario transition-colors hover:text-texto"
                    >
                      {link.rotulo}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
          ))}
        </div>

        <div className="mt-14 border-t border-contorno pt-6">
          <p className="text-sm text-texto-secundario">
            &copy; {ano} {marca.nome}. Todos os direitos reservados.
          </p>
        </div>
      </div>
    </footer>
  )
}
