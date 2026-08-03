# Frontend do Prisma

Landing React com entrada autenticada conectada ao backend Django local.

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

O login usa e-mail e senha, guarda o access token apenas em memoria e depende
do cookie HttpOnly de refresh emitido pelo backend.

## Producao

O frontend esta publicado em `https://frontend-three-ecru-55.vercel.app`. O
build de producao usa `VITE_API_URL=/api/v1`; `vercel.json` encaminha as rotas
da SPA e `api/proxy.ts` faz a ponte same-origin para a API publica do Railway.

Para publicar manualmente:

```bash
vercel deploy --prod --yes --build-env VITE_API_URL=/api/v1
```

## Template original

A landing pública do PrismaTest, implementada em React, TypeScript, Vite,
Tailwind CSS e Motion. O layout é mobile-first e a aplicação visual é
servida junto com as telas HTML demonstrativas em `/app/`.

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

As telas demonstrativas são mantidas em `../mockup/` e sincronizadas para
`public/app/` por `python ../scripts/sincronizar-app.py`. A pasta `public/app/`
é uma cópia derivada e não é a fonte de edição.

O frontend não implementa autenticação, regras de negócio, chamadas ao
OpenRouter ou persistência em servidor. Esses comportamentos dependem do
backend ainda não iniciado neste repositório.
