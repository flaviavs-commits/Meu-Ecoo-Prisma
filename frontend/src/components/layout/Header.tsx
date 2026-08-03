import { useEffect, useState } from 'react'
import { Button } from '../ui/Button'
import { LogoComNome } from '../ui/Logo'
import { navegacao } from '../../content/landing'
import { ENTRADA_APP } from '../../content/destinos'

/** Topbar responsiva com menu colapsavel em telas pequenas. */
export function Header() {
  const [aberto, setAberto] = useState(false)
  const [rolou, setRolou] = useState(false)

  useEffect(() => {
    const aoRolar = () => setRolou(window.scrollY > 8)
    aoRolar()
    window.addEventListener('scroll', aoRolar, { passive: true })
    return () => window.removeEventListener('scroll', aoRolar)
  }, [])

  return (
    <header
      className={[
        // Linha nítida de largura total, em grafite suavizado
        'sticky top-0 z-50 border-b border-contorno-forte transition-colors duration-300',
        rolou ? 'bg-fundo/70 backdrop-blur-sm' : 'bg-fundo/85',
      ].join(' ')}
    >
      {/*
        Logo a esquerda, acoes a direita, nav no centro do viewport.

        A nav e posicionada em absoluto de proposito: com flex-1 ela
        ficaria centrada no ESPACO QUE SOBRA entre as laterais, e como
        o bloco da direita ("Entrar" + botao) e bem mais largo que o
        logo, isso a empurrava visivelmente para a direita. Em absoluto
        ela se alinha ao centro real da barra, independente das laterais.

        Sem max-w no container: o header ocupa a largura toda para o
        logo encostar na margem, em vez de seguir o container
        centralizado que as secoes de conteudo usam.
      */}
      <div className="relative flex w-full items-center justify-between gap-4 px-4 py-4 sm:gap-8 sm:px-8 sm:py-5">
        <a href="#inicio" className="shrink-0 text-texto">
          <LogoComNome />
        </a>

        <nav
          aria-label="Principal"
          className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-8 md:flex"
        >
          {navegacao.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="text-[15px] text-texto transition-colors hover:text-marca"
            >
              {item.rotulo}
            </a>
          ))}
        </nav>

        <div className="hidden shrink-0 items-center gap-6 md:flex">
          {/* Vai direto a tela inicial da aplicacao, nao a uma ancora */}
          <a
            href={ENTRADA_APP}
            className="fonte-display text-xs font-bold tracking-[0.14em] text-texto uppercase transition-colors hover:text-marca"
          >
            Entrar
          </a>
          <Button size="md" href="#comecar">
            Começar grátis
          </Button>
        </div>

        <button
          type="button"
          className="grid min-h-11 min-w-11 place-items-center rounded-lg text-texto transition-colors hover:bg-superficie-alt md:hidden"
          aria-expanded={aberto}
          aria-controls="menu-mobile"
          aria-label={aberto ? 'Fechar menu' : 'Abrir menu'}
          onClick={() => setAberto((v) => !v)}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            {aberto ? (
              <path
                d="M6 6l12 12M18 6L6 18"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            ) : (
              <path
                d="M4 7h16M4 12h16M4 17h16"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            )}
          </svg>
        </button>
      </div>

      {aberto && (
        <div
          id="menu-mobile"
          className="border-t border-borda bg-superficie px-4 py-4 sm:px-6 md:hidden"
        >
          <nav aria-label="Principal (mobile)" className="flex flex-col gap-1">
            {navegacao.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={() => setAberto(false)}
                className="flex min-h-11 items-center rounded-lg px-3 py-2.5 text-texto-secundario transition-colors hover:bg-superficie-alt hover:text-texto"
              >
                {item.rotulo}
              </a>
            ))}
          </nav>
          <div className="mt-4 flex flex-col gap-2">
            <Button variant="secondary" href={ENTRADA_APP}>
              Entrar
            </Button>
            <Button href="#comecar">Começar grátis</Button>
          </div>
        </div>
      )}
    </header>
  )
}
