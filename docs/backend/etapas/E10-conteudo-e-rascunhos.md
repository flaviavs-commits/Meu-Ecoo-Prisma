# E10 - Conteudo e rascunhos

> **Status:** BLOQUEADA · **Responsavel:** Claude (sessao 2026-08-03)
> **Depende de:** E04, E08 · **Destrava:** -
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Modelar material didatico e prova, e implementar a regra que sustenta a
responsabilidade pedagogica do produto: **conteudo gerado por IA nasce rascunho
e so vira oficial por ato explicito do professor.**

## 2. Pre-requisitos

- E04 `CONCLUIDA` (mixin de acao destrutiva + auditoria)
- E08 `CONCLUIDA` (model `Arquivo`)
- `mockup/professor.html` - a tela real do professor

## 3. Escopo

**Entra:** `Material`, `Prova`, `Questao`, ciclo rascunho -> oficial, vinculo com
arquivo e turma, permissoes.

**Nao entra:** a geracao em si (vem do gateway de E06 e dos repositorios
satelites de E13). Aqui se modela **o que acontece com o resultado**.

## 4. Decisao travada: o conteudo de IA nasce rascunho

Registrada em 2026-07-16 no [`IA.md`](../../../IA.md) e reafirmada no
alinhamento de 2026-08-01. **Nao e detalhe de interface - e regra de backend.**

Por que: uma prova gerada por IA que valesse automaticamente como avaliacao
oficial transferiria a responsabilidade pedagogica da escola para um modelo de
linguagem. O professor precisa poder ler, corrigir e assumir o conteudo antes de
ele valer.

Consequencias obrigatorias:

- todo conteudo com `origem = IA` entra como `RASCUNHO`;
- **nao existe** caminho que crie conteudo `OFICIAL` direto;
- a transicao e explicita, autenticada, auditada e feita por quem tem
  permissao.

## 5. Como fazer

### 5.1 Entidades

```text
Material   conteudo de estudo; pode ter Arquivo (E08); vinculado a turma/disciplina
Prova      avaliacao; tem status e origem
Questao    pertence a uma prova; enunciado, alternativas, gabarito
```

Campos de estado, em `Prova` e `Material`:

| Campo | Valores |
|-------|---------|
| `status` | `RASCUNHO`, `OFICIAL`, `ARQUIVADO` |
| `origem` | `MANUAL`, `IA` |
| `revisado_por` | Preenchido na transicao |
| `revisado_em` | Preenchido na transicao |

`origem` e `status` sao **independentes**: conteudo manual tambem pode ficar em
rascunho enquanto o professor escreve.

### 5.2 A transicao rascunho -> oficial

E uma das tres acoes destrutivas da [visao geral](../VISAO-GERAL.md). Usa o
mixin de E04, sem variacao:

```
POST /api/v1/provas/57/oficializar/
{ "confirmacao": true, "motivo": "revisei as 10 questoes e corrigi a 4" }
```

Regras:

- so o autor ou o diretor pode oficializar (matriz de E04);
- prova ja `OFICIAL` -> `409` (conflito de estado), nao 400;
- prova sem questao -> `422`;
- a transicao grava `revisado_por`, `revisado_em` e auditoria;
- **e irreversivel por caminho normal.** Voltar a rascunho, se for permitido,
  e outra acao destrutiva, com seu proprio registro.

Nao existe `PATCH {"status": "OFICIAL"}`. Se existir, a regra vazou.

### 5.3 Gabarito - o que nao pode vazar

Questao tem gabarito. O aluno **nao** pode receber isso antes de responder.

Isso e falha de serializacao, nao de permissao de rota: o mesmo model, servido
com o serializer errado, entrega a resposta da prova. Use serializers
**diferentes** para professor e aluno - nunca um serializer com campo
condicional cheio de `if`, que e onde o erro se esconde.

Teste explicito: o JSON que o aluno recebe **nao contem** a chave do gabarito.

### 5.4 Vinculo com arquivo

Material pode ter um `Arquivo` (E08). Nao reimplemente upload - use o que ja
existe. O arquivo herda a restricao de acesso do material.

### 5.5 Permissoes

| Acao | Aluno | Professor | Diretor |
|------|:-----:|:---------:|:-------:|
| Ver material da sua turma | sim | sim | sim |
| Criar/editar material | nao | sim | sim |
| Ver prova em rascunho | **nao** | autor e diretor | sim |
| Ver prova oficial da sua turma | sim (sem gabarito) | sim | sim |
| Oficializar | nao | autor | sim |

Aluno **nunca** ve rascunho. Rascunho e trabalho em andamento, pode conter erro
grosseiro gerado por IA.

### 5.6 TDD - ordem sugerida

1. Conteudo criado com `origem=IA` nasce `RASCUNHO` - sempre.
2. Nao existe caminho que crie `OFICIAL` direto - inclusive via `PATCH`.
3. Oficializar sem `confirmacao` -> 400.
4. Oficializar sem `motivo` -> 400.
5. Oficializar prova sem questao -> 422.
6. Oficializar prova ja oficial -> 409.
7. Oficializar grava `revisado_por`, `revisado_em` e auditoria.
8. Professor que nao e autor nao oficializa -> 403.
9. Aluno nao ve prova em rascunho -> 404.
10. **JSON servido ao aluno nao contem gabarito.**
11. Material de outra instituicao -> 404.

## 6. Contrato de saida

- `Material`, `Prova`, `Questao` migrados
- ciclo rascunho -> oficial implementado e auditado
- serializers separados por perfil, gabarito protegido
- vinculo com `Arquivo` de E08

Quando a geracao real por IA existir (E06 + E13), ela cria conteudo **aqui**,
sempre como rascunho. O contrato ja esta pronto para isso.

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Gabarito vazando para o aluno | Serializers separados + teste 10 |
| `PATCH` burlando a transicao | `status` nao e campo editavel. Teste 2. |
| Aluno vendo rascunho de IA com erro | Rascunho invisivel ao aluno. Teste 9. |
| Oficializacao sem rastro | Auditoria embutida no mixin de E04 |
| Reimplementar upload | Use `Arquivo` de E08 |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Peguei E10 e chequei as dependencias antes de codar - protocolo
  manda conferir "Depende de" antes de tocar em qualquer etapa - `git status`
  e `ls` confirmaram: nao existe pasta `backend/` no repositorio (E01 nunca
  criou), e E02, E03, E04 e E08 estao todas `NAO INICIADA` no
  `docs/backend/README.md`. Ou seja, nao ha model, nao ha auth, nao ha
  multi-tenancy, nao ha `Arquivo` - a base inteira que E10 usa (mixin de acao
  destrutiva de E04, model `Arquivo` de E08) nao existe em codigo.
  Decisao: nao vou implementar E01/E02/E04/E08 "de passagem" para me
  desbloquear - o protocolo (`PROTOCOLO-DO-AGENTE.md`, secao 4 e secao 1)
  probe isso explicitamente, e outros agentes podem estar trabalhando nelas
  em paralelo no mesmo canvas. Marquei esta etapa como `BLOQUEADA` em vez de
  simular progresso.
  Proximo passo concreto para quem retomar: confirmar no README se algum
  agente ja pegou E01/E02/E03/E04/E08; se sim, esperar essas ficarem
  `CONCLUIDA` antes de reabrir E10; se nao, considerar pegar E01 (fundacao)
  primeiro, que e o gargalo real do projeto - nada mais destrava sem ela.

## 9. Criterio de pronto

- [ ] Os 11 testes do item 5.6 passam - saida real no diario
- [ ] Nenhum caminho cria conteudo oficial direto - verificado, inclusive `PATCH`
- [ ] JSON do aluno sem gabarito - verificado no corpo real da resposta
- [ ] Oficializacao auditada - conferido no banco
- [ ] Prova ja oficial responde 409, nao 400
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] `IA.md` atualizado confirmando a regra rascunho -> oficial em codigo
- [ ] Commit feito, so com arquivos desta etapa
