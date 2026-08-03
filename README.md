# PrismaTest

Implementacao web da plataforma de estudos com IA para instituicoes de ensino: OpenRouter como motor de IA, creditos por assinatura e memoria persistente por aluno.

> **Estado atual: fundação visual concluída.** A landing pública, a entrada de perfis, o login demonstrativo e as áreas visuais de aluno, professor e diretor estão implementados. A interface é mobile-first, oferece cinco idiomas com preferência persistente e fecha o seletor após a escolha. O backend, a autenticação real e o gateway de IA ainda não existem neste repositório.

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
├── docs/                   # Constituicao de modularidade e outros documentos do projeto
└── doktor SystemDesign/    # Padroes de qualidade (copia sincronizada, nao versionada)
```

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

Há verificações automatizadas de qualidade visual e estrutural, embora ainda não exista uma suíte de testes de regras de negócio. O frontend usa Playwright para validar rotas, idiomas, persistência da preferência, ausência de overflow em viewports móveis e erros de console; `scripts/verificar-i18n.py` valida as chaves dos cinco dicionários. Os comandos e resultados executados ficam em [IA.md](IA.md), na seção "Testes importantes".

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

> **Não há autenticação real.** Qualquer pessoa acessa qualquer área: o
> "Entrar" e o login são navegação demonstrativa, não controle de acesso.
> A autenticação real depende do backend e ainda não foi implementada.

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
