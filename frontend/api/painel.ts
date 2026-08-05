// Ponte same-origin do painel Django e dos estaticos administrativos.
//
// Este proxy e separado do proxy da API porque o painel devolve HTML e usa
// sessao/cookie. Ainda assim, a funcao valida caminho e metodo antes de
// encaminhar qualquer requisicao direta a `/api/painel`.

const ORIGEM_FALLBACK = 'https://api-production-8b58.up.railway.app'

function origemDaApi(): string {
  const origem = process.env.PRISMA_API_ORIGIN ?? ORIGEM_FALLBACK
  return origem.replace(/\/$/, '')
}

function rotaPermitida(caminho: string, metodo: string): boolean {
  if (!caminho || caminho.startsWith('/') || caminho.includes('\\') || caminho.includes('?')) {
    return false
  }

  const segmentos = caminho.split('/')
  if (segmentos.some((segmento, indice) => {
    const finalVazio = indice === segmentos.length - 1 && segmento === ''
    return (!finalVazio && !segmento) || segmento === '.' || segmento === '..'
  })) {
    return false
  }

  if (caminho.startsWith('static/')) {
    return metodo === 'GET' || metodo === 'HEAD'
  }

  if (caminho.startsWith('painel/') || caminho.startsWith('backoffice/')) {
    return metodo === 'GET' || metodo === 'HEAD' || metodo === 'POST'
  }

  return false
}

function copiarCabecalhos(resposta: Response): Headers {
  const cabecalhos = new Headers()
  for (const nome of [
    'cache-control',
    'content-disposition',
    'content-type',
    'location',
    'vary',
    'x-frame-options',
  ]) {
    const valor = resposta.headers.get(nome)
    if (valor) cabecalhos.set(nome, valor)
  }
  for (const cookie of resposta.headers.getSetCookie()) {
    cabecalhos.append('set-cookie', cookie)
  }
  return cabecalhos
}

function prepararCabecalhos(request: Request): Headers {
  const cabecalhos = new Headers(request.headers)
  cabecalhos.delete('content-length')
  cabecalhos.delete('host')
  return cabecalhos
}

function respostaErro(status: number, mensagem: string): Response {
  return new Response(mensagem, {
    status,
    headers: { 'content-type': 'text/plain; charset=utf-8' },
  })
}

export default {
  async fetch(request: Request): Promise<Response> {
    const urlRecebida = new URL(request.url)
    const caminho = urlRecebida.searchParams.get('path') ?? ''

    if (!rotaPermitida(caminho, request.method)) {
      const prefixoValido = caminho.startsWith('static/') || caminho.startsWith('painel/') || caminho.startsWith('backoffice/')
      return respostaErro(prefixoValido ? 405 : 404, prefixoValido ? 'Metodo nao permitido.' : 'Rota nao encontrada.')
    }

    const parametros = new URLSearchParams(urlRecebida.search)
    parametros.delete('path')
    const consulta = parametros.toString()
    const urlApi = `${origemDaApi()}/${caminho}${consulta ? `?${consulta}` : ''}`
    const corpo = request.method === 'GET' || request.method === 'HEAD'
      ? undefined
      : await request.arrayBuffer()
    const resposta = await fetch(urlApi, {
      method: request.method,
      headers: prepararCabecalhos(request),
      body: corpo,
    })

    return new Response(await resposta.arrayBuffer(), {
      status: resposta.status,
      headers: copiarCabecalhos(resposta),
    })
  },
}
