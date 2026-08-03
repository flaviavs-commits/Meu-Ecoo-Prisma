# Frontend do PrismaTest

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
