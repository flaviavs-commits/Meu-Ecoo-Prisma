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

## Template original

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.
