// Ponte same-origin entre a Vercel e a API Django no Railway.
//
// Duas garantias de seguranca que este arquivo precisa manter, mesmo que
// `vercel.json` ja restrinja as rotas publicas que chegam aqui:
// 1. Allowlist propria de caminho+metodo - `vercel.json` so controla como o
//    NAVEGADOR chega ate `/api/proxy`; nada impede uma chamada direta a
//    `/api/proxy?path=qualquer-coisa`, que bypassaria aquele encaminhamento.
//    Sem a allowlist abaixo, esta funcao seria um proxy aberto para
//    qualquer rota da API, na origem/metodo que quem chamar quiser.
// 2. Origem da API por variavel de ambiente, nao hardcoded - permite trocar
//    de dominio Railway (ex.: recriacao do servico) so ajustando a variavel
//    no painel da Vercel, sem editar codigo.
const ROTAS_PERMITIDAS: Record<string, ReadonlySet<string>> = {
  'health/': new Set(['GET']),
  'auth/login/': new Set(['POST']),
  'auth/refresh/': new Set(['POST']),
  'auth/eu/': new Set(['GET']),
  'auth/logout/': new Set(['POST']),
}

// Fallback temporario: dominio publico atual do servico `api` no Railway.
// Existe so para nao quebrar producao enquanto `PRISMA_API_ORIGIN` nao e
// configurada no painel da Vercel (Project Settings > Environment Variables).
// Assim que a variavel existir la, este fallback deixa de ser usado; se o
// dominio do servico mudar no futuro, atualize so a variavel na Vercel.
const ORIGEM_FALLBACK = 'https://api-production-8b58.up.railway.app'

function origemDaApi(): string {
  const origem = process.env.PRISMA_API_ORIGIN ?? ORIGEM_FALLBACK
  return origem.replace(/\/$/, '')
}

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

function respostaErro(status: number, mensagem: string): Response {
  return new Response(JSON.stringify({ erro: { mensagem } }), {
    status,
    headers: { 'content-type': 'application/json' },
  })
}

export default {
  async fetch(request: Request): Promise<Response> {
    const urlRecebida = new URL(request.url)
    const caminho = urlRecebida.searchParams.get('path') ?? ''
    const metodosPermitidos = ROTAS_PERMITIDAS[caminho]

    if (!metodosPermitidos) {
      return respostaErro(404, 'Rota nao encontrada.')
    }
    if (!metodosPermitidos.has(request.method)) {
      return respostaErro(405, 'Metodo nao permitido para esta rota.')
    }

    const origem = origemDaApi()
    const parametros = new URLSearchParams(urlRecebida.search)
    parametros.delete('path')
    const consulta = parametros.toString()
    const urlApi = `${origem}/api/v1/${caminho}${consulta ? `?${consulta}` : ''}`
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
