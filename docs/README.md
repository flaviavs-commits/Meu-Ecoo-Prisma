# Documentacao do Prisma

Mapa do que vive em `docs/`. Abra so o que a sua tarefa exige - a
[constituicao de modularidade](CONSTITUICAO-MODULARIDADE.md) vale tambem para
leitura de documento, nao so para codigo.

| Arquivo / pasta | Do que trata | Quando abrir |
|-----------------|--------------|--------------|
| [`CONSTITUICAO-MODULARIDADE.md`](CONSTITUICAO-MODULARIDADE.md) | Regra estrutural: um arquivo, uma responsabilidade | Antes de refatorar ou criar estrutura de pastas |
| [`backend/`](backend/) | System design do backend, dividido em etapas independentes | Qualquer trabalho de backend |

## Backend - por onde comecar

O backend ainda nao existe em codigo. O desenho esta pronto e dividido em
**13 etapas**, cada uma num arquivo proprio, para que agentes diferentes possam
trabalhar em paralelo sem se atropelar.

**Se voce e um agente que acabou de chegar, leia nesta ordem:**

1. [`backend/PROTOCOLO-DO-AGENTE.md`](backend/PROTOCOLO-DO-AGENTE.md) - como trabalhar aqui. Curto e obrigatorio.
2. [`backend/README.md`](backend/README.md) - painel das etapas: o que ja foi feito, o que esta livre, o que depende do que.
3. O arquivo da **sua** etapa em [`backend/etapas/`](backend/etapas/) - e so ele.

Nao leia as 13 etapas para trabalhar em uma. Cada arquivo de etapa carrega o
contexto necessario para ser executado sozinho.

## Documentacao geral do projeto

Fora de `docs/`, mas parte do mesmo conjunto:

| Arquivo | Papel |
|---------|-------|
| [`../README.md`](../README.md) | O que o projeto e, como rodar, como validar |
| [`../AGENTS.md`](../AGENTS.md) | Roteiro de IA: o que ler por tipo de tarefa |
| [`../IA.md`](../IA.md) | Linha do tempo tecnica: decisoes datadas, bugs, validacoes |
