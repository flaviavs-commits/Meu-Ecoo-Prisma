# PrismaTest

Implementacao web da plataforma de estudos com IA para instituicoes de ensino: OpenRouter como motor de IA, creditos por assinatura e memoria persistente por aluno.

> **Status: Fase 0 - fundacao.** A landing page publica esta implementada, com a identidade visual do documento UX/UI aplicada. O backend ainda nao existe em codigo, mas ja tem o desenho completo em [`docs/backend/`](docs/backend/), dividido em 13 etapas independentes. A landing (`frontend/`) e os mockups das telas por perfil (`mockup/`) vivem neste mesmo repositorio - a concepcao do produto e os mockups viviam num repositorio separado no inicio do projeto, mas hoje moram aqui.

**Divisao de trabalho:** Andre no frontend, Felipe no backend.

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
| Deploy | Railway | Hospedagem do backend |

Toda chamada de IA passa pelo gateway do backend. O frontend nunca fala com o OpenRouter diretamente.

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
├── mockup/                 # Telas de aluno, professor e diretor (fonte da verdade, HTML estatico)
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

O backend ainda nao foi escrito. O desenho esta pronto e dividido em etapas que
podem ser tocadas **em paralelo, por pessoas ou agentes diferentes** - cada
etapa e um arquivo que serve ao mesmo tempo de especificacao e de diario de
trabalho.

Comece por [`docs/backend/README.md`](docs/backend/README.md). A primeira etapa
a ser executada e a E01 (fundacao do projeto Django); ela destrava as demais.

## Como rodar

Requisitos: Node.js 20+ e Python 3.10+.

```bash
python start_app.py
```

Isso abre uma **janela** (o HUD) com o estado do ambiente ao vivo -
servidor, dependencias, telas, npm - e as acoes em botoes: **Rodar o
site**, **Abrir no navegador**, **Instalar dependencias**, **Sincronizar
aplicacao**, **Gerar build**, **Validar**, **Configurar porta** e **Parar
servidor**. A saida dos comandos aparece no painel de baixo.

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

O site fica em `http://localhost:5173`.

## Como validar

Pelo botao **Validar** do HUD, ou direto:

```bash
cd frontend
npm run lint     # oxlint
npm run build    # tsc + vite build
```

Ainda nao ha teste automatizado: a landing e UI visual sem regra de negocio, caso em que o guia minimo de qualidade aceita verificacao manual registrada. As verificacoes executadas estao em [IA.md](IA.md), secao "Testes importantes". Testes automatizados entram junto com a logica de negocio (autenticacao, creditos, gateway de IA).

## Landing e aplicacao

Sao duas partes deste mesmo repositorio:

| | Onde vive | O que e |
|---|---|---|
| **Landing** | `frontend/src/` | vitrine publica, em React |
| **Aplicacao** | `mockup/` | telas de aluno, professor e diretor (HTML estatico) |

Ao clicar em "Entrar", a landing abre a tela inicial da aplicacao,
que faz a escolha de perfil.

### Sincronizar a aplicacao

As telas sao mantidas em `mockup/`. Para trazer a versao atual para o Vite:

```bash
python scripts/sincronizar-app.py
```

Isso copia as telas para `frontend/public/app/`, que o Vite serve em
`/app/`. **Rode de novo sempre que as telas mudarem la** - a pasta e
uma copia derivada, ignorada pelo git.

O script tambem ajusta o link interno `landing.html`, que nao existe
mais aqui, para a raiz do site.

> **Nao ha autenticacao.** Qualquer pessoa acessa qualquer area: o
> "Entrar" e navegacao, nao controle de acesso. O login real entra
> com o backend. Quando existir, basta trocar `ENTRADA_APP` em
> `frontend/src/content/destinos.ts` - todos os botoes leem de la.

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
