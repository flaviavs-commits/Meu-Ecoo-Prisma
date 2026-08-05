# Frontend do Prisma

Landing React com a aplicação HTML definitiva conectada ao backend Django local.

## Desenvolvimento

```bash
npm install
cp .env.example .env.local
npm run dev
```

O Vite fica em `http://localhost:5173` quando a porta esta livre. A API
padrao e `http://127.0.0.1:8000/api/v1`; altere `VITE_API_URL` em `.env.local`
se necessario.

Comandos de validacao:

```bash
npm test
npm run lint
npm run build
```

O login definitivo em `/app/login.html` usa e-mail e senha, envia o access
token somente no cabeçalho das chamadas e depende do cookie HttpOnly de refresh
emitido pelo backend.

## Producao

O frontend esta publicado em `https://frontend-three-ecru-55.vercel.app`. O
build de producao usa `VITE_API_URL=/api/v1`; `vercel.json` encaminha as rotas
da SPA e `api/proxy.ts` faz a ponte same-origin para a API publica do Railway.
O favicon Prisma e publicado em SVG, PNG e ICO para cobrir navegadores e
clientes que procuram o caminho tradicional `/favicon.ico`.

`api/proxy.ts` so encaminha as rotas explicitamente listadas em sua propria
allowlist (`health/`, `auth/login/`, `auth/refresh/`, `auth/eu/`,
`auth/logout/`), cada uma com o metodo HTTP permitido - isso existe alem do
que `vercel.json` ja restringe, porque uma chamada direta a
`/api/proxy?path=...` bypassaria aquele encaminhamento se a funcao nao
validasse de novo. A origem da API vem de `PRISMA_API_ORIGIN` (variavel de
ambiente do projeto na Vercel, nao do `.env` do Vite - essa variavel roda no
servidor da funcao, nunca no bundle do navegador); enquanto ela nao estiver
configurada la, o codigo cai num fallback com o dominio Railway atual, so
para nao quebrar producao. Configurar `PRISMA_API_ORIGIN` no painel da Vercel
(Project Settings > Environment Variables) e o passo que falta para remover
esse fallback e trocar de dominio Railway (ex.: recriacao do servico) sem
editar codigo.

Para publicar manualmente:

```bash
vercel deploy --prod --yes --build-env VITE_API_URL=/api/v1
```

## Aplicação definitiva

A landing pública do PrismaTest, implementada em React, TypeScript, Vite,
Tailwind CSS e Motion. O layout é mobile-first e a aplicação visual é
servida junto com as telas HTML definitivas em `/app/`.

## Desenvolvimento

Na raiz do repositório, o caminho recomendado é `python start_app.py`, que
abre o HUD do projeto. Para trabalhar diretamente no frontend:

```bash
cd frontend
npm install
npm run dev
```

## Validação

```bash
cd frontend
npm run lint
npm run build
```

As telas definitivas são mantidas em `app/`. O `prebuild` executa
`scripts/sincronizar-app.mjs` para copiá-las a `public/app/`, incluindo a
publicação na Vercel quando o projeto usa `frontend/` como Root Directory.
Também é possível sincronizar manualmente pela automação Python da raiz.

O frontend não implementa autenticação, regras de negócio, chamadas ao
OpenRouter ou persistência em servidor. Esses comportamentos dependem do
backend ainda não iniciado neste repositório.
