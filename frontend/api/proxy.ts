const API_ORIGIN = 'https://api-production-8b58.up.railway.app'

function copiarCabecalhos(resposta: Response): Headers {
  const cabecalhos = new Headers()
  for (const nome of ['cache-control', 'content-type', 'location', 'vary', 'set-cookie']) {
    const valor = resposta.headers.get(nome)
    if (valor) cabecalhos.set(nome, valor)
  }
  return cabecalhos
}

function prepararCabecalhos(request: Request): Headers {
  const cabecalhos = new Headers(request.headers)
  cabecalhos.delete('content-length')
  cabecalhos.delete('host')
  return cabecalhos
}

export default {
  async fetch(request: Request): Promise<Response> {
    const urlRecebida = new URL(request.url)
    const caminho = urlRecebida.searchParams.get('path') ?? ''
    const parametros = new URLSearchParams(urlRecebida.search)
    parametros.delete('path')
    const consulta = parametros.toString()
    const urlApi = `${API_ORIGIN}/api/v1/${caminho}${consulta ? `?${consulta}` : ''}`
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
