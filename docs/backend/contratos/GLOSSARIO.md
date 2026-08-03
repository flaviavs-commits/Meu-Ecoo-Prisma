# Contrato: glossario de dominio

> Um nome, um significado. Consulte antes de batizar model, campo, rota ou
> servico. Nome inconsistente e divida que so cresce.
>
> O codigo fala **portugues** no dominio - o produto, os usuarios e as telas
> falam portugues, e traduzir so na fronteira gera erro de traducao.

## Pessoas e organizacao

| Termo | Significa | Nao confundir com |
|-------|-----------|-------------------|
| **Instituicao** | A escola ou universidade que assina. E a raiz do tenant. | "cliente", "conta", "escola" - use sempre `Instituicao` no codigo |
| **Usuario** | Qualquer pessoa que faz login | Nao use "conta" para pessoa |
| **Perfil** | O papel do usuario: `ALUNO`, `PROFESSOR` ou `DIRETOR` | Nao e "role", "tipo" nem "cargo" no codigo |
| **Aluno** | Perfil que estuda | |
| **Professor** | Perfil que ensina e corrige | Nao use "tutor" - `Tutor` e a IA, nao a pessoa |
| **Diretor** | Perfil que administra a instituicao e distribui creditos | Nao e "admin" - admin e a equipe interna |
| **Equipe interna** | Nos. Superusuarios sem instituicao. | Nunca chame de "diretor" |

## Academico

| Termo | Significa |
|-------|-----------|
| **Turma** | Grupo de alunos de uma instituicao. Nunca "workspace" - esse termo e residuo do modelo antigo e foi removido do produto. |
| **Matricula** | O vinculo entre um usuario e uma turma |
| **Disciplina** | Materia ensinada |
| **Nota** | Avaliacao lancada. Tem `origem`: `MANUAL` ou `IA`. |
| **Falta** | Ausencia registrada |

## Creditos

| Termo | Significa |
|-------|-----------|
| **Credito** | A unidade interna de consumo de IA. **Nao e dinheiro** e nunca deve ser exibido como moeda. |
| **Lancamento** | Um registro imutavel de entrada ou saida de credito. E a fonte da verdade. |
| **Saldo** | Resultado da soma dos lancamentos. **Nunca uma coluna.** |
| **Alocacao** | O diretor destinando parte do pool da instituicao a um perfil ou turma |
| **Debito** | Lancamento negativo, gerado por uma chamada de IA bem-sucedida |
| **Estorno** | Lancamento contrario que corrige outro. Nunca se apaga um lancamento. |

## IA

| Termo | Significa |
|-------|-----------|
| **Motor de IA** | O provedor externo. Hoje, OpenRouter. |
| **Gateway** | A camada do backend por onde **toda** chamada de IA passa. O frontend nunca fala com o provedor. |
| **Provedor** | Adaptador de um motor especifico. Substituivel. |
| **Classe de tarefa** | O tipo de trabalho pedido a IA (tutoria, geracao, correcao, resumo). Define qual modelo e usado. |
| **Chamada** | Um uso registrado do gateway, com custo e resultado |
| **Tutor** | A experiencia de estudo com IA do aluno. E a IA, nao uma pessoa. |

## Conteudo e memoria

| Termo | Significa |
|-------|-----------|
| **Material** | Conteudo de estudo (texto, PDF, audio) |
| **Prova** | Avaliacao com questoes |
| **Rascunho** | Estado inicial de todo conteudo gerado por IA. Nao vale como oficial. |
| **Oficial** | Estado apos revisao explicita do professor. So aqui vira nota/prova de verdade. |
| **Conversa** | O log bruto do dialogo entre aluno e tutor |
| **Memoria consolidada** | Resumo datado e imutavel do que o aluno estudou. Compactavel com o tempo. |

## Termos proibidos

Aparecem em codigo ou tela antigos e **nao devem ser reintroduzidos**:

| Termo | Por que sumiu |
|-------|---------------|
| **Workspace** | Vocabulario da era em que o produto era vendido ao usuario individual. Hoje e **Turma**. |
| **Criar conta / cadastro** | Nao existe autocadastro. A instituicao cadastra. |
| **Plano Prisma / Pro / Ultra** | Planos individuais da era antiga. O backend nao modela plano individual. |
| **Tutor** como pessoa | O professor e **Professor**. Tutor e a IA. |

## Ingles vs portugues

| Onde | Idioma |
|------|--------|
| Model, campo, rota, servico de dominio | **Portugues** |
| Termo tecnico sem traducao boa | Ingles: `token`, `cache`, `endpoint`, `middleware`, `queryset` |
| Nome de biblioteca e API externa | Como a biblioteca chama |
| Comentario e docstring | Portugues |

Regra pratica: se um professor da escola entenderia a palavra, ela vai em
portugues. Se e vocabulario de programador, pode ficar em ingles.

## Estado do canvas

- [2026-08-03] **Identidade:** `/Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/contratos/GLOSSARIO.md`.
- [2026-08-03] **Estado:** aguardando decisão de alocação para iniciar uma etapa de código do MVP. A fundação E01 está concluída; E02 está atribuída a outro agente e bloqueada no painel, enquanto E05, E08, E12 e E13 possuem trabalho paralelo não concluído. Nenhum arquivo de código foi alterado nesta sessão para evitar conflito entre agentes.
- [2026-08-03] **Validação:** `git status --short` confirmou alterações não relacionadas já presentes; a estrutura de backend e os contratos de E02 foram lidos. O guia mínimo do Felixo foi consultado na fonte oficial do repositório `Felipe-Alcantara/Felixo-System-Design` porque a cópia local não existe.
- [2026-08-03] **Retomada por** `/Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/contratos/GLOSSARIO.md`: o painel foi rechecado após a reinicialização dos agentes. Não há etapa livre e sem dependências para este nó; E02 continua bloqueada e atribuída, E03 depende dela, e E12/E13 já têm responsáveis. Nenhum código ou arquivo de outro agente foi alterado; estado final desta retomada: **bloqueado aguardando liberação/decisão de alocação**.
