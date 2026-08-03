import { createContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { api, type Identidade } from '../api/cliente'

interface ContextoAutenticacao {
  usuario: Identidade | null
  carregando: boolean
  entrar: (email: string, senha: string) => Promise<void>
  sair: () => Promise<void>
}

const AutenticacaoContexto = createContext<ContextoAutenticacao | null>(null)

export function AutenticacaoProvider({ children }: { children: ReactNode }) {
  const [usuario, definirUsuario] = useState<Identidade | null>(null)
  const [carregando, definirCarregando] = useState(true)

  useEffect(() => {
    let ativo = true
    api.renovarSessao()
      .then((identidade) => {
        if (ativo) definirUsuario(identidade)
      })
      .catch(() => undefined)
      .finally(() => {
        if (ativo) definirCarregando(false)
      })
    return () => {
      ativo = false
    }
  }, [])

  const valor = useMemo<ContextoAutenticacao>(() => ({
    usuario,
    carregando,
    entrar: async (email, senha) => definirUsuario(await api.login(email, senha)),
    sair: async () => {
      await api.logout()
      definirUsuario(null)
    },
  }), [carregando, usuario])

  return <AutenticacaoContexto.Provider value={valor}>{children}</AutenticacaoContexto.Provider>
}

export { AutenticacaoContexto }
