# PrismaTest

Implementacao web da plataforma de estudos com IA para instituicoes de ensino: OpenRouter como motor de IA, creditos por assinatura e memoria persistente por aluno.

> **Estado atual: fundação visual e backend MVP concluídos.** A landing pública, a entrada de perfis, o login real (`/entrar`, Django/DRF) e as áreas de aluno, professor e diretor (mockup HTML, mobile-first, cinco idiomas, modal de Configurações e chat premium do Tutor de IA) estão implementados. O backend Django ja possui fundacao, autenticacao, multitenancy, creditos, IA, memoria, arquivos, academico, conteudo e onboarding administrativo, validado localmente com SQLite (PostgreSQL/Railway em producao). Falta conectar a identidade autenticada as telas estaticas de `/app/` e fechar a validacao remota de multi-tenancy (E02).

**Divisão de trabalho:** o frontend visual está neste repositório; o backend ainda não foi iniciado aqui.

## Sobre

A instituicao assina a plataforma e recebe creditos de IA, distribuidos pelo diretor entre professores e alunos:

| Perfil | Foco | Principais ferramentas |
|--------|------|------------------------|
| Aluno | Estudar | Tutor de IA com memoria, gerador de textos de estudo, simulados, notas e faltas |
| Professor | Ensinar | Geracao e correcao de provas, banco de conteudo, material didatico, lancamento de notas |
| Diretor | Administrar | Dashboards de desempenho, gestao de usuarios e turmas, distribuicao de creditos |

## Stack

| Camada | Tecnologia | Papel |
|--------|-----------|-------|
| Frontend | React + TypeScript + Vite + Tailwind | SPA com areas separadas por perfil |
| Backend | Django + Django REST Framework | API, regras de negocio, contabilidade de creditos |
| IA | OpenRouter | Acesso multi-modelo (geracao, correcao, tutoria) |
| Banco | PostgreSQL | Usuarios, conteudo, notas, faltas, creditos, memoria |
| Deploy frontend | Vercel | Landing e entrada autenticada |
| Deploy backend | Railway | API Django e PostgreSQL |

Toda chamada de IA passa pelo gateway do backend. O frontend nunca fala com o OpenRouter diretamente.

## URLs de producao

- Frontend: <https://frontend-three-ecru-55.vercel.app>
- API: <https://api-production-8b58.up.railway.app>

O build da Vercel usa `VITE_API_URL=/api/v1`. As rotas de autenticacao e o
health check passam por uma funcao same-origin em `frontend/api/proxy.ts`, que
encaminha as requisicoes para o Railway e preserva o cookie HttpOnly de refresh.
O frontend nao depende de variaveis privadas no navegador.

## Estrutura

```
PrismaTest/
├── AGENTS.md               # Roteiro para agentes de IA neste projeto
├── IA.md                   # Memoria operacional: decisoes, estado e validacoes
├── README.md
├── start_app.py            # Gatilho: abre o HUD
├── scripts/
│   ├── sincronizar-app.py  # Traz as telas do Estudo-com-IA
│   └── hud/                # O HUD, um modulo por responsabilidade
│       ├── tokens.py       # Paleta, tipografia e medidas
│       ├── layout.py       # Monta a janela
│       ├── status.py       # Mede o ambiente e pinta o card
│       ├── console.py      # Terminal embutido
│       ├── acoes.py        # O que cada card faz
│       └── widgets/        # Um arquivo por widget desenhado
├── frontend/               # React + TypeScript + Vite + Tailwind
│   ├── public/app/         # Telas da aplicacao (copia derivada, ignorada)
│   └── src/
│       ├── components/
│       │   ├── ui/         # Base (Button, Card, Secao) e animacao
│       │   │               # (Animar, Titulo3D, Atmosfera, Card3D)
│       │   ├── layout/     # Header, Rodape
│       │   └── feature/    # Secoes da landing
│       ├── content/        # Copy e destino da aplicacao
│       └── index.css       # Tokens de design e regra de cor (@theme)
├── app/                    # Telas definitivas da aplicação (HTML estático)
├── docs/
│   ├── CONSTITUICAO-MODULARIDADE.md
│   └── backend/            # System design do backend, em 13 etapas independentes
│       ├── README.md       # Painel: o que esta livre, o que depende do que
│       ├── PROTOCOLO-DO-AGENTE.md
│       ├── contratos/      # Regras que todas as etapas respeitam
│       └── etapas/         # E01..E13 - uma etapa por arquivo
└── doktor SystemDesign/    # Padroes de qualidade (copia sincronizada, nao versionada)
```

## Backend

A fundacao (E01) esta pronta: projeto Django + DRF rodando, conectado ao
Postgres do Railway, com `pytest` e o endpoint de saude respondendo. O restante
do dominio esta dividido em etapas que podem ser tocadas **em paralelo, por
pessoas ou agentes diferentes** - cada etapa e um arquivo que serve ao mesmo
tempo de especificacao e de diario de trabalho.

Comece por [`docs/backend/README.md`](docs/backend/README.md) para ver o que
esta livre e o que depende do que.

### Como rodar o backend localmente

```bash
cd backend
python3.11 -m venv .venv          # Python 3.12 preferido; 3.11 usado nesta maquina por falta do 3.12
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env              # mantenha DATABASE_URL em SQLite no desenvolvimento
.venv/bin/python manage.py migrate
.venv/bin/python manage.py check
.venv/bin/pytest
```

O SQLite e a escolha segura para desenvolvimento e TDD local. Nao e necessario
Railway para rodar ou validar o MVP. Em producao, o frontend roda na Vercel e a
API usa PostgreSQL no Railway com as variaveis do ambiente correspondente.

### Criar uma instituicao nova

O onboarding interno e transacional: ou cria a instituicao, o diretor e o
credito inicial, ou nao cria nada. O diretor recebe uma conta sem senha
utilizavel para seguir o fluxo de definicao de senha.

```bash
.venv/bin/python manage.py criar_instituicao \\
  --nome "Colegio Exemplo" \\
  --documento "00.000.000/0001-00" \\
  --diretor-email "diretor@exemplo.edu.br" \\
  --diretor-nome "Nome do Diretor" \\
  --creditos-iniciais 100000
```

O Admin interno fica em `DJANGO_ADMIN_URL` (padrao local: `/backoffice/`),
fora de `/admin/`, e exige `is_staff`. Diretores de escola nao recebem acesso
ao Admin.

O superusuario entra pelo login em `/painel/`, que e a area de controle da
plataforma. Nessa area, os atalhos **Instituicoes** e **Contas teste** permitem
criar uma instituicao com credito inicial e contas academicas ativas para
validar as telas de aluno, professor e diretor. Cada operacao e transacional,
auditada e nao concede privilegios administrativos a conta de teste. Depois de
criar uma conta, use o e-mail e a senha definidos em `/entrar`; o perfil da
conta determina a tela academica aberta.

## Como rodar

Requisitos: Node.js 20+ e Python 3.10+.

```bash
python start_app.py
```

Isso abre uma **janela** (o HUD) com o estado do ambiente ao vivo -
frontend, backend, dependencias, telas, npm - e as acoes em botoes: **Rodar
aplicacao**, **Abrir no navegador**, **Rodar backend**, **Instalar
dependencias**, **Sincronizar aplicacao**, **Gerar build**, **Validar**,
**Configurar porta** e **Fechar portas**. A saida dos comandos aparece no
painel de baixo. Ao rodar a aplicacao, o HUD prepara as migracoes em SQLite
local e sobe o Django e o Vite em conjunto.

O painel de baixo e um **console funcional**: digite qualquer comando de
terminal e tecle Enter. Comeca em `frontend/`, entao `npm run dev` e
`npm install` funcionam direto. Aceita `cd`, `pwd`, `clear`, `exit`,
historico com as setas e Ctrl+C para interromper.

> O HUD precisa de interface grafica. Em ambiente sem display (SSH,
> container, CI) ele nao abre - use os comandos npm abaixo. O motivo
> desse desvio em relacao ao guia do Doktor esta em [IA.md](IA.md).

Para rodar direto, sem o HUD:

```bash
cd frontend
npm install
npm run dev
```

O site fica em `http://localhost:5173` (ou na porta exibida pelo Vite se a
porta padrao estiver ocupada).

O login da landing fica em `/entrar` e usa `VITE_API_URL` (padrao:
`http://127.0.0.1:8000/api/v1`) para conversar com o backend Django. O token de
acesso permanece somente em memoria; o refresh usa cookie HttpOnly.

## Como validar

Pelo botao **Validar** do HUD, ou direto:

```bash
cd frontend
npm test       # Vitest
npm run lint     # oxlint
npm run build    # tsc + vite build
cd ../backend
.venv/bin/pytest -q
```

Há verificações automatizadas de qualidade visual e estrutural no frontend: Playwright valida rotas, idiomas, persistência da preferência, ausência de overflow em viewports móveis e erros de console; `scripts/verificar-i18n.py` valida as chaves dos cinco dicionários. O backend tem cobertura por `pytest`. Os comandos e resultados executados ficam em [IA.md](IA.md), na seção "Testes importantes".

## Landing e aplicacao

Sao duas partes deste mesmo repositorio:

| | Onde vive | O que e |
|---|---|---|
| **Landing** | `frontend/src/` | vitrine publica, em React |
| **Aplicacao** | `frontend/app/` | telas definitivas de aluno, professor e diretor (HTML estatico) |

Ao clicar em "Entrar", a landing abre `/entrar`, que autentica por e-mail e
senha contra o backend. O access token fica somente em memoria no navegador;
o refresh usa cookie HttpOnly. A tela de perfil da aplicacao continua sendo
servida em `/app/` para o proximo ciclo de integracao.

### Sincronizar a aplicacao

As telas sao mantidas em `frontend/app/`. Para trazer a versao atual para o Vite:

```bash
python scripts/sincronizar-app.py
```

Isso copia as telas para `frontend/public/app/`, que o Vite serve em
`/app/`. **Rode de novo sempre que as telas mudarem la** - a pasta e
uma copia derivada, ignorada pelo git.

O controle de acesso da API ja existe. As telas estaticas de `/app/` ainda
precisam receber a identidade autenticada e as protecoes de rota no proximo
ciclo; nao devem ser tratadas como uma area protegida concluida.

## Mexer no HUD

O `start_app.py` e so o gatilho. O HUD vive em `scripts/hud/`, com um
modulo por responsabilidade - abra so o que a mudanca exige:

| Para mudar... | Abra |
|---------------|------|
| Cor, fonte ou espacamento | `scripts/hud/tokens.py` |
| Posicao das secoes na janela | `scripts/hud/layout.py` |
| O que um botao faz | `scripts/hud/acoes.py` |
| Comportamento do console | `scripts/hud/console.py` |
| Aparencia de um card, modal ou barra | `scripts/hud/widgets/<nome>.py` |
| O que o card de status mede | `scripts/hud/ambiente.py` |

O mapa completo esta em `scripts/hud/__init__.py`. A regra que mantem
assim: [docs/CONSTITUICAO-MODULARIDADE.md](docs/CONSTITUICAO-MODULARIDADE.md).

## Comportamento da interface

O layout é mobile-first e foi verificado em telas estreitas e largas. A
preferência de idioma é salva em `localStorage` sob a chave `prisma-lang`;
ela é reaplicada nas telas de entrada, login, aluno, professor e diretor até
que o usuário escolha outro idioma. Ao selecionar uma opção, o dropdown e o
fundo de bloqueio fecham automaticamente.

O conteúdo da aplicação é uma demonstração estática. Ações como gerar
materiais, responder ao tutor e confirmar correções alteram apenas o estado
visual local; não há chamadas a API nem persistência em servidor.

## Personalizar a landing

O texto fica em `frontend/src/content/landing.ts`, separado dos componentes. As cores e a tipografia ficam em `frontend/src/index.css`, no bloco `@theme`.

## Padroes de qualidade

Este projeto segue o [Doktor System-Design](https://github.com/AndreGustavoms/Doktor-SystemDesign). Os padroes ficam em `doktor SystemDesign/`, uma copia sincronizada e **nao versionada** (esta no `.gitignore`).

Para trazer ou atualizar essa pasta:

```powershell
doktor
```

Se o comando nao existir, instale-o uma vez:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<caminho-do-Doktor>\scripts\powershell\install-doktor-powershell.ps1"
```

Mudancas nos padroes vao no repositorio Doktor System-Design, nunca nesta copia local.

## Licenca

A definir.
