# Backend do Prisma - painel de etapas

> **Este arquivo e o ponto de encontro dos agentes.** Ele diz o que ja foi
> feito, o que esta livre e o que depende do que. O detalhe de cada etapa mora
> no arquivo dela.

**Antes de pegar uma etapa, leia o [protocolo do agente](PROTOCOLO-DO-AGENTE.md).**
Sao 5 minutos e evitam retrabalho.

## Estado do backend

O backend ja existe em codigo e as etapas E01, E03-E11 foram implementadas e
validadas localmente com SQLite. A E02 continua marcada como bloqueada por sua
validacao remota/multi-tenant pendente; nao altere seus arquivos sem registrar
a decisao no diario. A integracao atual do frontend usa `/api/v1/auth/` e o
endpoint de saude. Em producao, o frontend esta na Vercel e usa uma ponte
same-origin para a API publica do Railway; o endurecimento do novo container
Railway aguarda a regularizacao da assinatura.

**Estado deste no:** as etapas de backend necessarias ao MVP local estao
entregues. O trabalho corrente e a integracao frontend/backend e a validacao
do HUD em `scripts/hud/`; novas etapas de dominio devem ser abertas somente
quando houver escopo definido no painel.

## Como escolher uma etapa

1. Ache uma linha com status `NAO INICIADA` cuja coluna "Depende de" ja esteja
   `CONCLUIDA`.
2. Escreva seu nome na coluna "Responsavel" e mude o status para `EM ANDAMENTO`
   - **aqui e no cabecalho do arquivo da etapa**.
3. Trabalhe so no arquivo da sua etapa, escrevendo no diario dele conforme
   avanca.

> **Cuidado com conflito:** varios agentes editam este arquivo. Altere **apenas
> a sua linha** da tabela. Nao reformate a tabela inteira, nao reordene, nao
> "arrume de passagem" a linha de outro.

## Tabela de etapas

| # | Etapa | Status | Responsavel | Depende de | Destrava |
|---|-------|--------|-------------|-----------|----------|
| E01 | [Fundacao do projeto](etapas/E01-fundacao-do-projeto.md) | CONCLUIDA | Claude (API-CONVENCOES.md) | - | todas |
| E02 | [Nucleo de dados e multi-tenancy](etapas/E02-nucleo-de-dados-e-multitenancy.md) | BLOQUEADA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/Responsavel por todas as etapas | E01 | E03..E11 |
| E03 | [Autenticacao JWT](etapas/E03-autenticacao-jwt.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E02 | E04 |
| E04 | [Autorizacao e perfis](etapas/E04-autorizacao-e-perfis.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E03 | E05, E09, E10, E11 |
| E05 | [Creditos - ledger](etapas/E05-creditos-ledger.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E04 | E06 |
| E06 | [Gateway de IA - interface](etapas/E06-gateway-de-ia.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E05 | E07 |
| E07 | [Memoria e conversas do tutor](etapas/E07-memoria-e-conversas.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E06 | - |
| E08 | [Upload de materiais](etapas/E08-upload-de-materiais.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E02 | E10 |
| E09 | [Academico - turmas, notas, faltas](etapas/E09-academico.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E04 | - |
| E10 | [Conteudo e rascunhos](etapas/E10-conteudo-e-rascunhos.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E04, E08 | - |
| E11 | [Admin e onboarding da escola](etapas/E11-admin-e-onboarding.md) | CONCLUIDA | /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md | E04 | - |
| E12 | [Infra Railway e deploy](etapas/E12-infra-railway-e-deploy.md) | AGUARDANDO DECISAO | Claude (agente de infra) | E01 | - |
| E13 | [API nos repos satelites](etapas/E13-api-nos-repos-satelites.md) | AGUARDANDO DECISAO | Claude (sessao 2026-08-03) | - | integracao real de E06 |
| E14 | [Painel operacional do superadmin](etapas/E14-painel-superadmin.md) | AGUARDANDO DECISÃO | Analizar o front do Prisma | E04, E11 | operacao interna do backend |

## Ordem e paralelismo

`E01` e `E02` sao gargalo: quase tudo depende delas, e elas sao sequenciais
entre si. Depois de `E02`, abre-se paralelismo real.

```text
E01 ─┬─> E02 ─┬─> E03 ──> E04 ─┬─> E05 ──> E06 ──> E07
     │        │                 ├─> E09
     │        │                 ├─> E10 <── E08
     │        └─> E08           └─> E11
     └─> E12

E13  (independente - acontece em OUTROS repositorios)
```

**Podem comecar em paralelo desde o inicio:** `E12` (infra, so precisa de E01) e
`E13` (outros repositorios, nao depende de nada aqui).

**Depois de E04, podem correr juntas:** `E05`, `E09`, `E10`, `E11`.

## O que cada etapa entrega, em uma linha

| # | Entrega |
|---|---------|
| E01 | Projeto Django rodando, conectado ao Postgres do Railway, com pytest e health check |
| E02 | `Instituicao`, `Usuario` customizado e o mecanismo que impede vazamento entre escolas |
| E03 | Login, refresh, logout e troca de senha por JWT, com rate limit |
| E04 | Quem pode o que: perfis, permissao por objeto e o padrao de confirmacao destrutiva |
| E05 | Saldo de creditos por ledger imutavel, alocacao pelo diretor, regra de bloqueio |
| E06 | Gateway de IA com adaptador substituivel e contabilidade de uso - sem chamada real |
| E07 | Conversa do tutor persistida e memoria consolidada compactavel |
| E08 | Upload de arquivo em disco, validado e isolado por instituicao |
| E09 | Turmas, matriculas, notas e faltas |
| E10 | Materiais e provas, com o ciclo rascunho -> oficial |
| E11 | Django Admin utilizavel para criar e operar a conta de uma escola |
| E12 | Deploy no Railway, variaveis, volume, health check em producao |
| E13 | `Estudo-IA-Resumo` e `Audiofy-Content-AI` expostos como API HTTP |
| E14 | Painel interno do superadmin, com usuarios, auditoria e troca de perfil |

## Documentos de apoio

| Documento | Papel |
|-----------|-------|
| [`PROTOCOLO-DO-AGENTE.md`](PROTOCOLO-DO-AGENTE.md) | Como trabalhar aqui. Obrigatorio. |
| [`VISAO-GERAL.md`](VISAO-GERAL.md) | Arquitetura e decisoes travadas |
| [`FERRAMENTAS-E-ECOSSISTEMA.md`](FERRAMENTAS-E-ECOSSISTEMA.md) | Railway, GitHub, Notion e os repositorios irmaos |
| [`contratos/`](contratos/) | Regras que todas as etapas respeitam |
