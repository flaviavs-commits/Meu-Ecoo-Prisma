export interface Identidade {
  id: number
  nome: string
  perfil: 'ALUNO' | 'PROFESSOR' | 'DIRETOR' | null
  instituicao_id: number | null
}

interface RespostaToken {
  access: string
}

interface RespostaErro {
  erro?: {
    codigo?: string
    mensagem?: string
  }
}

export class ErroApi extends Error {
  readonly status: number
  readonly codigo: string

  constructor(status: number, codigo: string, mensagem: string) {
    super(mensagem)
    this.name = 'ErroApi'
    this.status = status
    this.codigo = codigo
  }
}

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api/v1'
).replace(/\/$/, '')

let tokenDeAcesso: string | null = null

async function lerResposta<T>(resposta: Response): Promise<T> {
  const corpo = (await resposta.json().catch(() => ({}))) as T & RespostaErro
  if (resposta.ok) return corpo

  const erro = corpo.erro
  throw new ErroApi(
    resposta.status,
    erro?.codigo ?? 'erro',
    erro?.mensagem ?? 'Nao foi possivel concluir a requisicao.',
  )
}

async function requisitar<T>(
  caminho: string,
  init: RequestInit = {},
  autenticada = false,
): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  if (autenticada && tokenDeAcesso) {
    headers.set('Authorization', `Bearer ${tokenDeAcesso}`)
  }

  const resposta = await fetch(`${API_BASE_URL}${caminho}`, {
    ...init,
    headers,
    credentials: 'include',
  })
  return lerResposta<T>(resposta)
}

async function login(email: string, senha: string): Promise<Identidade> {
  const tokens = await requisitar<RespostaToken>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password: senha }),
  })
  tokenDeAcesso = tokens.access
  return requisitar<Identidade>('/auth/eu/', {}, true)
}

async function renovarSessao(): Promise<Identidade | null> {
  try {
    const tokens = await requisitar<RespostaToken>('/auth/refresh/', { method: 'POST' })
    tokenDeAcesso = tokens.access
    return requisitar<Identidade>('/auth/eu/', {}, true)
  } catch (erro) {
    if (erro instanceof ErroApi && erro.status === 401) {
      tokenDeAcesso = null
      return null
    }
    throw erro
  }
}

async function logout(): Promise<void> {
  await requisitar<void>('/auth/logout/', { method: 'POST' }).catch(() => undefined)
  tokenDeAcesso = null
}

export const api = { login, renovarSessao, logout }
