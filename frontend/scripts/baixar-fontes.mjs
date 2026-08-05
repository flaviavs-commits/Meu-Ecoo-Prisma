/**
 * Baixa e self-hospeda as fontes do Prisma.
 *
 * POR QUE SELF-HOSPEDAR
 *
 * A landing carregava as fontes por <link> para fonts.googleapis.com.
 * Isso custa caro no primeiro carregamento:
 *
 *   1. A folha externa BLOQUEIA a renderizacao - o navegador nao
 *      pinta nada ate baixa-la.
 *   2. Sao dois dominios novos (googleapis + gstatic): DNS, TCP e TLS
 *      para cada um, antes de o primeiro byte de fonte chegar.
 *   3. So depois de ler o CSS o navegador descobre a URL do .woff2 e
 *      comeca a baixar - uma cascata de tres idas e voltas.
 *
 * Servindo do proprio dominio, o @font-face ja esta no CSS que o
 * navegador tem em maos, os arquivos vem da mesma conexao ja aberta e
 * ganham hash no nome (cache imutavel).
 *
 * SUBSET: o Google devolve 23 @font-face (cirilico, grego, vietnamita
 * ...). Uma landing em pt-BR usa latin e latin-ext. Os outros 13
 * arquivos nunca seriam pintados - ficam de fora.
 *
 * PESOS: apenas os que a interface realmente renderiza, verificados no
 * navegador (getComputedStyle sobre todo elemento com texto proprio):
 *   Josefin Sans 400, 500, 700   Inter 400, 500
 * Inter 600 e Josefin 600 estavam sendo baixados sem nunca aparecer.
 *
 * FONTE VARIAVEL - por que deduplicamos por conteudo:
 *
 * O Google devolve o MESMO arquivo .woff2 para todos os pesos de uma
 * familia (é uma fonte variavel: um arquivo, eixo de peso continuo).
 * Salvar um arquivo por peso faria o navegador baixar tres copias
 * identicas de Josefin. Entao agrupamos por hash do conteudo e
 * declaramos uma FAIXA de peso (`font-weight: 400 700`), que e como
 * @font-face descreve fonte variavel.
 *
 * latin-ext fica no CSS mesmo sem o portugues precisar: `unicode-range`
 * faz o navegador so baixar o arquivo se algum caractere daquela faixa
 * aparecer na tela. Custa zero byte enquanto nao for usado e evita
 * texto quebrado se entrar um nome proprio com caractere eslavo.
 *
 * Rode de novo apenas se mudar peso ou familia:
 *   node scripts/baixar-fontes.mjs
 */
import { mkdir, writeFile, rm, readdir } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const AQUI = dirname(fileURLToPath(import.meta.url))
const DESTINO = join(AQUI, '..', 'src', 'fontes')

/** UA de Chrome moderno: sem isso o Google devolve .ttf em vez de .woff2. */
const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

const FONTE_URL =
  'https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@400;500;700&family=Inter:wght@400;500&display=swap'

/** Subsets que uma pagina em portugues realmente pinta. */
const SUBSETS_MANTIDOS = new Set(['latin', 'latin-ext'])

const css = await fetch(FONTE_URL, { headers: { 'User-Agent': UA } }).then((r) => {
  if (!r.ok) throw new Error(`Google Fonts respondeu ${r.status}`)
  return r.text()
})

/*
  O CSS vem como uma sequencia de:
    /* latin *\/
    @font-face { ... src: url(https://...woff2) ... }
  Casamos o comentario de subset junto com o bloco para poder filtrar.
*/
const blocos = [...css.matchAll(/\/\*\s*([a-z-]+)\s*\*\/\s*(@font-face\s*\{[^}]+\})/g)]
if (!blocos.length) throw new Error('Nao consegui interpretar o CSS do Google Fonts')

/*
  Limpa os .woff2 antigos um a um em vez de remover a pasta: em disco
  sincronizado (OneDrive) o rmdir falha com EBUSY enquanto o
  sincronizador segura o diretorio.
*/
await mkdir(DESTINO, { recursive: true })
for (const antigo of await readdir(DESTINO).catch(() => [])) {
  if (antigo.endsWith('.woff2')) await rm(join(DESTINO, antigo), { force: true })
}

/*
  Primeiro baixamos tudo que interessa e agrupamos por hash do
  conteudo. Cada grupo vira UM arquivo em disco e UMA regra
  @font-face com a faixa de peso que aquele arquivo cobre.
*/
const porConteudo = new Map()
let ignorados = 0

for (const [, subset, bloco] of blocos) {
  if (!SUBSETS_MANTIDOS.has(subset)) {
    ignorados++
    continue
  }

  const familia = bloco.match(/font-family:\s*'([^']+)'/)?.[1]
  const peso = Number(bloco.match(/font-weight:\s*(\d+)/)?.[1])
  const estilo = bloco.match(/font-style:\s*(\w+)/)?.[1] ?? 'normal'
  const faixa = bloco.match(/unicode-range:\s*([^;]+);/)?.[1]?.trim()
  const url = bloco.match(/url\((https:[^)]+\.woff2)\)/)?.[1]
  if (!familia || !peso || !url) continue

  const bytes = Buffer.from(await fetch(url).then((r) => r.arrayBuffer()))
  const hash = createHash('sha1').update(bytes).digest('hex')

  const grupo = porConteudo.get(hash)
  if (grupo) {
    // Mesmo arquivo servindo outro peso: so amplia a faixa.
    grupo.pesos.push(peso)
  } else {
    porConteudo.set(hash, { familia, estilo, faixa, subset, bytes, pesos: [peso] })
  }
}

const regras = []
let totalBytes = 0

for (const g of porConteudo.values()) {
  const min = Math.min(...g.pesos)
  const max = Math.max(...g.pesos)
  const arquivo = `${g.familia.toLowerCase().replace(/\s+/g, '-')}-${g.subset}.woff2`

  await writeFile(join(DESTINO, arquivo), g.bytes)
  totalBytes += g.bytes.length

  regras.push(
    `@font-face {\n` +
      `  font-family: '${g.familia}';\n` +
      `  font-style: ${g.estilo};\n` +
      /* Faixa (ex.: "400 700") descreve fonte variavel: um arquivo
         atende todos os pesos entre os extremos. */
      `  font-weight: ${min === max ? min : `${min} ${max}`};\n` +
      /* swap: o texto aparece já na fonte do sistema e troca quando a
         real chega - nunca fica invisivel esperando download. */
      `  font-display: swap;\n` +
      `  src: url('./${arquivo}') format('woff2');\n` +
      (g.faixa ? `  unicode-range: ${g.faixa};\n` : '') +
      `}`,
  )
}

const cabecalho = `/*
  GERADO POR scripts/baixar-fontes.mjs - NAO EDITE A MAO.
  Para mudar peso ou familia, altere o script e rode de novo.
*/\n\n`

await writeFile(join(DESTINO, 'fontes.css'), cabecalho + regras.join('\n\n') + '\n')

console.log(
  `${porConteudo.size} arquivos woff2 unicos (${(totalBytes / 1024).toFixed(1)} kB), ` +
    `${ignorados} subsets fora do escopo ignorados.`,
)
for (const g of porConteudo.values()) {
  console.log(
    `  ${g.familia} ${g.subset}: pesos ${[...new Set(g.pesos)].sort().join('/')} ` +
      `-> 1 arquivo de ${(g.bytes.length / 1024).toFixed(1)} kB`,
  )
}
