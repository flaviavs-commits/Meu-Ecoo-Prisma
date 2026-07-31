# AGENTS.md - Roteiro de IA do Projeto

> **O que e**: Arquivo raiz para orientar agentes de IA neste projeto.
>
> **Objetivo**: Manter a IA direcionada, preservar qualidade minima e reduzir consumo de contexto. A IA deve ler o minimo necessario para a tarefa, sem abrir documentacao "por garantia".

---

## 0. Contexto deste projeto

O **PrismaTest** e a plataforma SaaS de estudos para instituicoes de ensino, com OpenRouter como motor de IA, creditos por assinatura e memoria persistente por aluno.

Este repositorio contem o **codigo real**: a landing publica (`frontend/`) e as telas de aluno, professor e diretor (`mockup/`). No inicio do projeto, concepcao e mockup viviam num repositorio separado (`Estudo-com-IA`) - hoje moram aqui, no mesmo lugar do codigo.

Os padroes de qualidade ficam sincronizados em `doktor SystemDesign/`, atualizaveis com o comando `doktor` rodado na raiz.

## 1. Principio central

Este arquivo nao e um framework rigido. Ele e um roteador leve:

- define o contrato minimo antes de qualquer entrega;
- aponta quais documentos abrir por tipo de tarefa;
- evita reler guias grandes sem necessidade;
- registra onde a IA deve atualizar contexto, decisoes e validacoes.

## 2. Leitura obrigatoria

1. Leia sempre `doktor SystemDesign/core/GUIA_MINIMO_QUALIDADE.md`.
2. Antes de alterar arquivos, leia `IA.md` - comece pela secao "Estado atual (resumo vivo)", nao pelo historico completo.
3. Use `README.md` para entender setup, comandos e objetivo publico.
4. Depois disso, abra apenas os documentos indicados na secao 3. Uma tarefa comum precisa de no maximo 1-2 documentos alem do guia minimo. Ter mais guias opcionais disponiveis no acervo nao significa ler mais - abra no maximo 1 guia opcional por tarefa.
5. Antes de editar manualmente, procure automacao existente (script, comando, instalador). Reutilize ou estenda antes de editar na mao; se editar manualmente, registre o motivo.

## 3. Roteiro por tipo de tarefa

Todos os caminhos abaixo sao relativos a `doktor SystemDesign/`.

| Se a tarefa e... | Leia alem do guia minimo |
|------------------|--------------------------|
| Frontend, UI ou UX | `core/DESIGN_SYSTEM_FRONTEND.md` |
| Backend, API, banco ou regra de negocio | `core/DESIGN_SYSTEM_BACKEND.md` |
| API REST, contratos ou status codes | `core/DESIGN_SYSTEM_API_REST.md` |
| Estrutura, camadas ou organizacao de codigo | `core/DESIGN_SYSTEM_ARQUITETURA.md` |
| Seguranca, secrets, auth ou dados sensiveis | `core/DESIGN_SYSTEM_SEGURANCA.md` |
| Testes, cobertura, mocks ou nomenclatura | `core/DESIGN_SYSTEM_TESTES.md` |
| README ou documentacao | `core/DESIGN_SYSTEM_README.md` |
| Stack, arquitetura ou decisao tecnica | `docs/STACK-E-ARQUITETURA.md` |
| Qualquer programa rodavel (web, CLI, automacao, script) | `core/GUIA-START-APP-SCRIPT.md` |
| Qual nivel de IA usar ou como economizar contexto | `core/DESIGN_SYSTEM_ECONOMIA_IA.md` |
| Chamada de LLM, agente ou gateway de IA | `guias/integracao/GUIA-INTEGRACAO-LLM-E-AGENTES.md` |
| Login por token, JWT ou OAuth | `guias/backend/GUIA-AUTENTICACAO-JWT-OAUTH.md` |
| Deploy no Railway | `guias/integracao/GUIA-DEPLOY-RAILWAY.md` |
| Validar projeto pronto | `docs/CHECKLIST-PROJETO-PRONTO.md` |
| Refatorar, quebrar arquivo ou criar estrutura de pastas | `docs/CONSTITUICAO-MODULARIDADE.md` (na raiz deste projeto, nao no Doktor) |
| Funcionalidade especifica | Guia opcional correspondente, somente se existir e casar com a tarefa |

## 4. Modularidade - regra estrutural obrigatoria

**Cada arquivo tem UMA responsabilidade.** Regra permanente, com
prioridade sobre preferencia pessoal de organizacao.

Texto completo em [`docs/CONSTITUICAO-MODULARIDADE.md`](docs/CONSTITUICAO-MODULARIDADE.md)
- leia antes de refatorar ou criar estrutura nova. O resumo abaixo basta
para tarefa comum.

O motivo e economico. Para trocar a cor de um botao num arquivo de 1700
linhas, a IA le 1700 linhas: gasta tempo, gasta token e arrisca mexer no
que nao devia. Se o botao mora num arquivo de 60 linhas, ela le 60.
**A prioridade nao e ter poucos arquivos - e ler pouco para consertar.**
40 arquivos de 80 linhas sao melhores que 1 de 3.000.

### Ao criar qualquer coisa, pergunte

> "Essa responsabilidade ja pertence exatamente a este arquivo?"

Se nao for um **sim absoluto**, crie um modulo novo. Na duvida entre
criar arquivo novo ou aumentar o existente, **crie o novo**.

### Proibido: arquivo deposito

`utils.ts`, `helpers.ts`, `misc.ts`, `common.ts`, `functions.ts`,
`services.ts` gigante, `components.tsx` com varios componentes.

Um componente por arquivo. Um hook por arquivo. Um contexto por arquivo.
Um tipo por arquivo. Nunca concentrar.

### Limites (alerta estrutural, nao proibicao)

| Tipo | Ideal | Maximo |
|------|-------|--------|
| Componente React | 120 | 200 |
| Hook | 80 | 150 |
| Modulo Python | 150 | 300 |
| Conteudo / CSS | 150 | 250 |
| Documento | 250 | 400 |

Dividir por **responsabilidade**, nao por contagem de linhas. Teste: o
arquivo cabe numa frase simples? "Esse arquivo desenha o Header." Se
precisar de **e**, **tambem**, **alem disso** - ha responsabilidades
demais.

### Onde cada coisa vive aqui

| O que e | Onde vai |
|---------|----------|
| Componente base reutilizavel | `frontend/src/components/ui/` |
| Estrutura de pagina | `frontend/src/components/layout/` |
| Secao com regra propria | `frontend/src/components/feature/` |
| Texto, copy, links | `frontend/src/content/` |
| Token de design, cor, fonte | `frontend/src/index.css` (`@theme`) |
| Automacao | `scripts/`, um arquivo por tarefa |

**Texto nunca fica dentro do componente.** Editar uma frase nao pode
exigir abrir JSX.

### Durante repair

Abra **apenas os arquivos necessarios**. E proibido reler o projeto
inteiro, modificar arquivo sem necessidade, centralizar codigo ou mover
responsabilidade para arquivo maior. Alteracao num componente toca
aquele componente.

### Debitos conhecidos

Ja violam a regra. Ao mexer neles, **quebre antes** em vez de aumentar -
mas nao quebre "de passagem" numa tarefa que nao os envolve: e mudanca
estrutural e merece commit proprio.

- `IA.md` (~360 linhas) - append-only. Passando de 400, arquivar os
  antigos **sem editar** em `docs/ia-archive/IA-ARCHIVE-<ano>.md`.

O `start_app.py` saiu desta lista em 2026-07-29: tinha 1716 linhas e
hoje e um gatilho de 48 que chama `scripts/hud/`. Para mexer no HUD,
abra o modulo da responsabilidade - o mapa esta em
`scripts/hud/__init__.py`, nao no `start_app.py`.

## 5. Regras praticas

- Nao leia documentos por garantia.
- Nao invente stack: este projeto ja definiu React + TypeScript + Vite + Tailwind no frontend e Django + DRF + PostgreSQL no backend.
- Ao mudar comportamento, comandos, estrutura ou decisao, atualize `README.md`, `IA.md` ou `docs/` no mesmo passo, em tempo real (nao deixe para o fim do trabalho).
- O `IA.md` e linha do tempo: nao apague registros antigos ao mudar uma decisao; adicione um novo registro datado com motivo e validacao.
- Todo programa rodavel entrega `start_app.py` na raiz como porta de entrada unica - nao flags de linha de comando. **Neste projeto o `start_app.py` e uma janela grafica (Tkinter), nao um menu de terminal**: desvio consciente do guia do Doktor, registrado em `IA.md` (2026-07-29). Nao "corrija" de volta para menu de terminal sem decisao explicita do Andre.
- Antes de usar uma API, biblioteca ou metodo, confirme que ela existe na versao instalada - nao presuma de memoria.
- Registre validacao objetiva com evidencia real de execucao: comando de teste rodado e saida observada, checklist manual, ou motivo de nao haver teste automatico. "Deve funcionar" nao e validacao.
- Prefira automacao a edicao manual quando ja existir script ou ferramenta reutilizavel para a mudanca.
- Ao versionar, use Conventional Commits: `tipo(escopo): descricao no imperativo`. Tipos validos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`. Cada commit e uma unidade coesa e separada - nao misture temas diferentes no mesmo commit.
- **A chave do OpenRouter e server-side e vive em variavel de ambiente.** Nunca no frontend, nunca no repositorio. Toda chamada de IA passa pelo gateway do backend.
- Nunca exponha segredo, token, dado pessoal ou caminho local privado em documentacao publica.

## 6. Criterio de pronto

Uma entrega so esta pronta quando outra pessoa ou outra IA consegue entender:

- o que mudou;
- por que mudou;
- como rodar;
- como validar;
- qual risco ou limite ainda existe.

E, pela constituicao de modularidade (secao 4):

- cada responsabilidade permanece isolada;
- nenhum arquivo virou "deposito";
- a alteracao exigiu ler apenas os arquivos realmente envolvidos;
- a estrutura continua modular;
- a proxima IA consegue modificar aquela parte sem analisar centenas de
  linhas desnecessarias.
