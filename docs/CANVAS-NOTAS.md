# Notas do canvas (coordenação entre agentes)

Este arquivo é o scratchpad compartilhado entre agentes rodando neste mesmo
diretório (`Meu-Ecoo-Prisma`). Antes de mexer em Railway (deploy, variáveis,
start command) ou em arquivos que outro agente possa estar editando, confira
aqui e deixe um registro do que você está fazendo.

## 2026-08-05 · Painel do prisma

**Em andamento:** ajustando o visual do `painel_admin` (Django, `/painel/`)
para usar os tokens oficiais do design system do Prisma
(`frontend/src/index.css`: creme/grafite/terracota/oliva/lavanda, Josefin
Sans nos títulos, Inter no corpo). Arquivos tocados:
`backend/painel_admin/static/painel_admin/painel.css`,
`backend/painel_admin/templates/painel_admin/*.html`.

**Já feito e publicado em produção hoje (service `api` no Railway,
`https://api-production-8b58.up.railway.app`):**
- Painel de superadmin (`/painel/`) fechado: 1ª e 2ª fatia (registros de
  auditoria, zerar créditos, desativar usuário), ver
  `docs/backend/etapas/E14-painel-superadmin.md`.
- Corrigido `DJANGO_ALLOWED_HOSTS` (bloqueava o healthcheck do Railway,
  deploys viviam falhando).
- Corrigido `LOGIN_URL` (painel sem login caía em 404 em vez do login do
  Django Admin).
- Adicionado `whitenoise` + `collectstatic` no start command (sem isso,
  `DEBUG=False` não servia nenhum CSS/JS estático — admin e painel ficavam
  sem estilo).
- Criado o primeiro superadmin em produção (`felipe@vitissouls.com`).

**Se você (outro agente) for mexer no serviço `api` do Railway agora:**
peça para eu (Painel do prisma) checar antes, ou ao menos rode
`railway status` primeiro — fizemos várias mudanças de config de serviço
(start command, variáveis) nas últimas horas e um redeploy concorrente pode
sobrescrever/conflitar.
