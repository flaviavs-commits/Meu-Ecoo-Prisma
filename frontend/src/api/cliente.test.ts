import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from './cliente'

describe('cliente da API de autenticacao', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    vi.stubGlobal('fetch', vi.fn())
  })

  it('envia e-mail e senha, preserva cookie e carrega a identidade', async () => {
    const fetchMock = vi.mocked(fetch)
    fetchMock
      .mockResolvedValueOnce(new Response(JSON.stringify({ access: 'access-token' }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        id: 4, nome: 'Ana', perfil: 'ALUNO', instituicao_id: 8,
      }), { status: 200 }))

    const identidade = await api.login('ana@escola.test', 'senha-segura')

    expect(identidade.nome).toBe('Ana')
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/auth/login/',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ email: 'ana@escola.test', password: 'senha-segura' }),
      }),
    )
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/auth/eu/',
      expect.objectContaining({
        credentials: 'include',
        headers: expect.any(Headers),
      }),
    )
  })

  it('converte erro padronizado do backend em ErroApi', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response(JSON.stringify({
      erro: { codigo: 'nao_autenticado', mensagem: 'Credenciais invalidas.' },
    }), { status: 401 }))

    await expect(api.login('ana@escola.test', 'errada')).rejects.toMatchObject({
      status: 401,
      codigo: 'nao_autenticado',
      message: 'Credenciais invalidas.',
    })
  })
})
