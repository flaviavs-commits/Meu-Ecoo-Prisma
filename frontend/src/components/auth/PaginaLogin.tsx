import { useState } from 'react'
import type { FormEvent } from 'react'
import { ErroApi } from '../../api/cliente'
import { useAutenticacao } from '../../auth/useAutenticacao'
import { autenticacao } from '../../content/autenticacao'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'

export function PaginaLogin() {
  const { usuario, carregando, entrar, sair } = useAutenticacao()
  const [email, definirEmail] = useState('')
  const [senha, definirSenha] = useState('')
  const [erro, definirErro] = useState('')
  const [enviando, definirEnviando] = useState(false)

  if (carregando) {
    return <main className="flex min-h-svh items-center justify-center bg-fundo text-texto">Carregando...</main>
  }

  if (usuario) {
    return (
      <main className="flex min-h-svh items-center justify-center bg-fundo px-6 py-16">
        <section className="w-full max-w-lg rounded-3xl border border-contorno bg-superficie p-8 shadow-sm sm:p-10">
          <p className="text-sm uppercase tracking-[0.14em] text-texto-secundario">Sessao ativa</p>
          <h1 className="fonte-display mt-3 text-4xl text-texto">Ola, {usuario.nome || 'estudante'}.</h1>
          <p className="mt-4 text-texto-secundario">Perfil: {usuario.perfil ?? 'nao definido'}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button href="/">Voltar para inicio</Button>
            <Button variant="secondary" onClick={() => void sair()}>Sair</Button>
          </div>
        </section>
      </main>
    )
  }

  async function submeter(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    definirErro('')
    definirEnviando(true)
    try {
      await entrar(email.trim(), senha)
    } catch (causa) {
      definirErro(causa instanceof ErroApi ? causa.message : autenticacao.erroPadrao)
    } finally {
      definirEnviando(false)
    }
  }

  return (
    <main className="flex min-h-svh items-center justify-center bg-superficie-alt px-6 py-16">
      <section className="w-full max-w-md rounded-3xl border border-contorno bg-fundo p-8 shadow-sm sm:p-10">
        <a href="/" className="text-sm text-texto-secundario transition-colors hover:text-marca">← {autenticacao.voltar}</a>
        <h1 className="fonte-display mt-10 text-4xl text-texto">{autenticacao.titulo}</h1>
        <p className="mt-4 leading-relaxed text-texto-secundario">{autenticacao.descricao}</p>
        <form className="mt-8 flex flex-col gap-5" onSubmit={submeter} noValidate>
          <Input
            label={autenticacao.email}
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(evento) => definirEmail(evento.target.value)}
          />
          <Input
            label={autenticacao.senha}
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={senha}
            onChange={(evento) => definirSenha(evento.target.value)}
          />
          {erro && <p role="alert" className="rounded-xl bg-erro/10 px-4 py-3 text-sm text-erro">{erro}</p>}
          <Button type="submit" disabled={enviando} className="mt-2 w-full">
            {enviando ? autenticacao.carregando : autenticacao.entrar}
          </Button>
        </form>
      </section>
    </main>
  )
}
