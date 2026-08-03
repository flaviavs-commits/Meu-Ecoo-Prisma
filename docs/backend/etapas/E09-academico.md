# E09 - Academico (turmas, notas, faltas)

> **Status:** CONCLUIDA · **Responsavel:** /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md
> **Depende de:** E04 · **Destrava:** -
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Modelar a vida escolar: turmas, quem esta em qual turma, disciplinas, notas e
faltas. E a base que o painel do professor e o dashboard do diretor consomem.

Roda em paralelo com E05, E10 e E11.

## 2. Pre-requisitos

- E04 `CONCLUIDA` (permissoes e escopo de instituicao prontos)
- [`../contratos/GLOSSARIO.md`](../contratos/GLOSSARIO.md) - **"Turma", nunca "workspace"**
- As telas `mockup/professor.html` e `mockup/diretor.html` - especificacao funcional real

## 3. Escopo

**Entra:** `Turma`, `Disciplina`, `Matricula`, `Nota`, `Falta`, endpoints de
CRUD e consulta, agregados para os paineis.

**Nao entra:** prova e material (E10), correcao por IA (E10 + E06).

## 4. Decisoes ja travadas

| Decisao | Valor |
|---------|-------|
| Nome | **Turma**. "Workspace" e vocabulario proibido - residuo do modelo antigo. |
| Nota gerada por IA | Nasce como rascunho. So vira oficial por acao do professor (E10). |
| Quem matricula | Diretor / secretaria. **Nunca** o aluno, e nunca por link publico. |

> A tela do professor ja teve "compartilhar workspace por link publico". Foi
> removida em 2026-07-31 por contradizer o modelo institucional. **Nao
> reintroduza** convite por link.

## 5. Como fazer

### 5.1 Entidades

```text
Disciplina    materia ensinada na instituicao
Turma         grupo de alunos; tem professor responsavel e disciplina
Matricula     vinculo aluno <-> turma (com data de entrada e saida)
Nota          aluno, disciplina, turma, valor, origem, avaliacao
Falta         aluno, turma, data, justificada
```

`Matricula` como entidade propria (nao um `ManyToMany` simples) porque o vinculo
tem historia: quando entrou, quando saiu, se esta ativo. Aluno transferido no
meio do ano nao pode simplesmente sumir da turma - a nota que ele tirou continua
existindo.

### 5.2 Regras que o **banco** garante

Regra que so vive no Python sera violada por um script ou uma migracao um dia:

- `UniqueConstraint`: o mesmo aluno nao se matricula duas vezes na mesma turma
  enquanto a matricula estiver ativa;
- `UniqueConstraint`: uma falta por aluno, por turma, por data;
- `CheckConstraint`: valor de nota dentro da faixa valida da instituicao;
- `on_delete` pensado: apagar uma turma **nao** pode apagar o historico de notas.
  Prefira `PROTECT`.

### 5.3 Faixa de nota - nao presuma 0 a 10

Universidade usa 0-10, escola pode usar conceito (A-E), curso tecnico usa 0-100.
Assumir 0-10 e travar o produto no primeiro cliente diferente.

Modele a faixa como **configuracao da instituicao** (`nota_minima`,
`nota_maxima`, ou escala nomeada). Se for simplificar por agora, **registre a
simplificacao no diario** como divida consciente - nao como fato.

### 5.4 Permissoes - refinando a matriz de E04

| Acao | Aluno | Professor | Diretor |
|------|:-----:|:---------:|:-------:|
| Ver as proprias notas/faltas | sim | - | - |
| Ver notas da turma | nao | so das suas turmas | sim |
| Lancar/editar nota | nao | so das suas turmas | sim |
| Registrar falta | nao | so das suas turmas | sim |
| Criar turma / matricular | nao | nao | sim |

"Suas turmas" e o ponto de atencao: professor de uma turma **nao** ve aluno de
outra. Isso e checagem por objeto (E04), nao so por perfil. **Teste de IDOR aqui
e obrigatorio.**

### 5.5 Historico de alteracao de nota

Nota alterada depois de lancada e assunto sensivel - toca a vida academica de
uma pessoa. Guarde quem alterou, quando e o valor anterior.

Reuse o `RegistroDeAuditoria` de E04 em vez de criar um mecanismo proprio.

### 5.6 Agregados para os paineis

Os paineis pedem numeros: media da turma, frequencia, alunos ativos, engajamento.

- calcule com agregacao no banco (`annotate`/`aggregate`), **nunca** em laco
  Python sobre todos os registros;
- cuidado com N+1: use `select_related`/`prefetch_related`;
- pagine tudo;
- teste com volume realista (uma instituicao com milhares de alunos), nao com
  tres registros.

### 5.7 TDD - ordem sugerida

1. Criar turma, matricular aluno, listar alunos da turma.
2. Matricula duplicada e recusada pelo banco.
3. Professor lanca nota na **sua** turma - sucesso.
4. Professor lanca nota em turma de **outro** professor -> 403.
5. Professor de outra instituicao -> 404.
6. Aluno ve so as proprias notas.
7. Aluno tentando ver nota de colega -> 403.
8. Nota fora da faixa e recusada.
9. Falta duplicada no mesmo dia e recusada.
10. Alteracao de nota grava auditoria com valor anterior.
11. Agregado de media da turma confere com calculo manual.

## 6. Contrato de saida

- `Disciplina`, `Turma`, `Matricula`, `Nota`, `Falta` migrados
- endpoints de CRUD com permissao por objeto
- agregados dos paineis com consulta eficiente
- alteracao de nota auditada

E10 usa `Turma` e `Disciplina` para vincular material e prova.

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| IDOR entre turmas | Checagem por objeto + testes 4 e 7 |
| Faixa de nota fixa em 0-10 | Configuravel por instituicao, ou divida registrada |
| Aluno transferido perdendo historico | `Matricula` com entrada/saida, `PROTECT` na FK |
| N+1 nos paineis | Agregacao no banco + teste com volume |
| "Workspace" voltando ao vocabulario | Glossario. Se aparecer, e bug. |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Peguei E09 e chequei as dependencias antes de comecar - protocolo
  manda conferir se "Depende de" esta CONCLUIDA. Resultado: a pasta `backend/`
  ainda nao existe no repositorio (so sera criada em E01) e E01, E02, E03 e E04
  estao todas `NAO INICIADA`. Nao ha projeto Django, `Usuario`, `Instituicao`,
  JWT nem permission classes para eu construir `Turma`/`Nota`/`Falta` em cima.
  Decisao: **nao** vou implementar E01-E04 "de passagem" para me desbloquear -
  o protocolo probe isso e corre o risco de conflitar com outro agente que
  esteja nessas etapas em paralelo no canvas. Status vira `BLOQUEADA`.
  Proximo passo real: assim que E04 estiver `CONCLUIDA` (ou pelo menos E01-E03,
  se eu decidir assumir o risco do contrato declarado de E04 antes dela fechar),
  retomo daqui seguindo o plano do item 5. Ate la, nao ha saida de codigo para
  validar.
- [2026-08-03] Retomei E09 como /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md - por que: E04 foi concluida e o usuario autorizou continuar localmente; como validei: li o glossario e o checklist TDD, mantendo o vocabulario `Turma` e sem reintroduzir links publicos de convite.
- [2026-08-03] Concluí E09 localmente como /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md - por que: expandi `Turma` e entreguei `Disciplina`, `Matricula`, `Nota`, `Falta`, escala institucional 0-10 e endpoints de consulta/lancamento; matricula segue exclusiva do diretor, professor fica limitado a turma responsavel e alteracao de nota audita valor anterior. Como validei: `DATABASE_URL=sqlite:///local-test.sqlite3 .venv/bin/pytest ./academico/tests/ -q` retornou `14 passed`; a suite transversal retornou `88 passed, 1 skipped` no SQLite e `89 passed` no PostgreSQL local; `sqlmigrate academico 0002` exibiu constraints de unicidade e check; `manage.py check` e `makemigrations --check --dry-run --noinput` passaram. A escala 0-10 fica registrada como simplificacao consciente até existir uma escala institucional diferente. Estado final: **CONCLUIDA localmente**.

## 9. Criterio de pronto

- [x] Os 11 cenarios do item 5.7 passam - `14 passed` incluindo endpoints
- [x] Teste de IDOR entre turmas/instituicoes existe e passa
- [x] Constraints estao **no banco**, nao so no Python - confirmado por `sqlmigrate`
- [x] Agregados sem N+1 - teste confirmou uma query
- [x] Alteracao de nota auditada - conferido no banco
- [x] Decisao sobre faixa de nota registrada - simplificacao 0-10
- [x] Nenhum arquivo passa de 300 linhas
- [x] Commit feito, somente depois de validar o escopo desta etapa
