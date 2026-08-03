# E04 - Autorizacao e perfis

> **Status:** BLOQUEADA · **Responsavel:** agente-canvas-E04
> **Depende de:** E03 · **Destrava:** E05, E09, E10, E11
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Definir **quem pode o que** - e entregar as ferramentas reutilizaveis que as
outras etapas vao usar para nao reinventar permissao cada uma do seu jeito.

E03 resolveu **quem a pessoa e**. Esta etapa resolve **o que ela pode fazer**.

## 2. Pre-requisitos

- E03 `CONCLUIDA`
- [`../contratos/API-CONVENCOES.md`](../contratos/API-CONVENCOES.md)
- [`../contratos/LGPD-E-DADOS-SENSIVEIS.md`](../contratos/LGPD-E-DADOS-SENSIVEIS.md)

## 3. Escopo

**Entra:** matriz de permissao dos 3 perfis, permission classes reutilizaveis,
protecao contra IDOR, escopo automatico de instituicao nas views, e o **padrao
de confirmacao para acao destrutiva**.

**Nao entra:** as regras especificas de cada dominio (quem ve qual nota e E09).
Aqui se entrega o **mecanismo**; cada etapa aplica.

## 4. Matriz de permissao

Ponto de partida. Cada etapa de dominio refina a sua linha e **registra a
diferenca no diario**.

| Acao | Aluno | Professor | Diretor |
|------|:-----:|:---------:|:-------:|
| Ver os proprios dados | sim | sim | sim |
| Ver dados de outro aluno | nao | so da sua turma | sim (sua instituicao) |
| Ver a propria nota / falta | sim | - | - |
| Lancar nota e falta | nao | sim (sua turma) | sim |
| Criar e editar material | nao | sim | sim |
| Tornar prova/nota **oficial** | nao | sim (autor) | sim |
| Usar o tutor de IA | sim | sim | sim |
| Ler conversa crua de aluno | so a sua | **nao** (ver LGPD) | **nao** (ver LGPD) |
| Ver consumo de credito da instituicao | nao | proprio | sim |
| **Alocar credito** | nao | nao | sim |
| Criar turma, matricular | nao | nao | sim |
| Convidar professor | nao | nao | sim |
| **Remover usuario** | nao | nao | sim |
| Criar instituicao | nao | nao | nao (so equipe interna) |

**Regra de ouro:** ninguem enxerga nada de outra instituicao. Nem o diretor.
Isso e anterior a esta matriz e vale sempre.

## 5. Como fazer

### 5.1 Permission classes - pequenas e combinaveis

Um arquivo por permissao (constituicao de modularidade). Evite uma classe
gigante com `if perfil == ...`.

```text
contas/permissoes/
├── e_aluno.py
├── e_professor.py
├── e_diretor.py
├── mesma_instituicao.py       # a mais importante
└── e_dono_do_objeto.py
```

Combine por composicao (`IsAuthenticated & EDiretor`), nao por heranca em
cadeia.

### 5.2 Escopo de instituicao nas views - automatico

E02 entregou o manager. Aqui isso vira comportamento padrao de view: um mixin
de `ViewSet` que filtra o queryset por `request.user.instituicao` **antes** de
qualquer coisa.

O padrao correto e "seguro por omissao": uma view nova ja nasce filtrada, e
sair do escopo exige ato deliberado e comentado.

### 5.3 IDOR - checar por objeto, nao so por rota

O erro classico: a rota exige "ser professor", o atacante e professor, troca o
id na URL e le a nota de aluno de outra turma.

- Sempre `check_object_permissions`.
- Objeto de outra instituicao responde **404, nao 403** (contrato de API,
  item 6). Isso e teste obrigatorio.
- Teste de IDOR faz parte do criterio de pronto de **toda** etapa de dominio.

### 5.4 Padrao de confirmacao destrutiva

As tres acoes destrutivas da [visao geral](../VISAO-GERAL.md) usam o mesmo
padrao, definido **aqui** e reusado sem variacao:

| Acao | Etapa que aplica |
|------|------------------|
| Zerar/remover creditos de perfil ou turma | [E05](E05-creditos-ledger.md) |
| Remover aluno ou professor da instituicao | [E11](E11-admin-e-onboarding.md) |
| Tornar prova/nota gerada por IA oficial | [E10](E10-conteudo-e-rascunhos.md) |

O padrao:

1. **`POST` numa sub-rota de acao**, nunca `DELETE` direto:
   `POST /api/v1/alunos/42/remover/`
2. Corpo exige `confirmacao: true` **e** `motivo` (texto nao vazio). Sem os
   dois, `400`.
3. **Registro de auditoria obrigatorio**: quem, o que, quando, sobre quem, com
   qual motivo. Sem auditoria, a acao nao acontece.
4. Efeito **reversivel** onde possivel: remover usuario e desativar, nao apagar.
   Estorno de credito e lancamento contrario, nao exclusao.
5. Resposta descreve o que foi feito, para a interface poder confirmar.

Entregue isso como um **mixin reutilizavel** + um model `RegistroDeAuditoria`.
Se cada etapa fizer do seu jeito, uma delas vai esquecer a auditoria.

> Considerar exigir a senha do diretor para acao destrutiva (re-autenticacao)?
> E mais seguro e comum em painel administrativo. Como afeta a interface,
> **registre a recomendacao e pergunte** em vez de decidir sozinho.

### 5.5 TDD - ordem sugerida

1. Aluno acessando rota de diretor -> 403.
2. Professor acessando aluno de **outra instituicao** -> 404 (nao 403).
3. Professor acessando aluno de outra turma da **mesma** instituicao -> 403.
4. Diretor acessando qualquer usuario da sua instituicao -> 200.
5. Acao destrutiva sem `confirmacao` -> 400.
6. Acao destrutiva sem `motivo` -> 400.
7. Acao destrutiva valida grava auditoria - conferido no banco.
8. View nova sem escopo explicito nao vaza - teste do mixin.

## 6. Contrato de saida

- permission classes prontas: `EAluno`, `EProfessor`, `EDiretor`,
  `MesmaInstituicao`, `EDonoDoObjeto`
- mixin de view que filtra por instituicao automaticamente
- mixin de acao destrutiva com confirmacao + motivo + auditoria
- model `RegistroDeAuditoria`
- regra "404, nao 403" implementada e testada

**Toda etapa seguinte usa estas ferramentas.** Criar permissao propria exige
registro do motivo no diario.

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| IDOR - o furo mais comum de API | Checagem por objeto + teste obrigatorio em toda etapa |
| Permissao so na rota | Mixin de escopo por omissao |
| Auditoria esquecida | Vem embutida no mixin, nao e opcional |
| Diretor virar superpoder | Diretor e limitado a **sua** instituicao. Teste isso explicitamente. |
| Re-autenticacao em acao destrutiva | Pendente de decisao humana - ver 5.4 |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Peguei E04, conferi dependencias antes de escrever qualquer
  codigo - protocolo item 4 exige isso. E03 (Autenticacao JWT) esta
  `NAO INICIADA`, e ela depende de E02, que esta `BLOQUEADA` por ausencia de
  E01. E01 (fundacao do projeto) esta `EM ANDAMENTO` por outro agente agora -
  nao existe ainda pasta `backend/` em codigo, nem `Usuario` customizado, nem
  DRF configurado. Sem isso nao ha onde pendurar `permission classes` reais
  (elas dependem do shape de `request.user.instituicao` que E02 vai definir).
  Verifiquei o trabalho dos outros agentes (`git log`, `git worktree list`,
  tabela do README): E02, E06, E07, E08 e E09 ja foram marcadas `BLOQUEADA`
  pelo mesmo motivo - so E05 optou por seguir contra o contrato assumido
  (risco registrado no diario dela). Decidi seguir o padrao da maioria em vez
  de inventar um formato de `Usuario`/multi-tenancy por conta propria, que
  poderia colidir com o que E01/E02 estao definindo agora mesmo em paralelo.
  Marquei o status desta etapa como `BLOQUEADA` e vou atualizar so a minha
  linha no README. Proximo passo assim que E03 estiver `CONCLUIDA`: seguir a
  secao 5 (permission classes por arquivo, mixin de escopo por instituicao,
  mixin de acao destrutiva + `RegistroDeAuditoria`) e a ordem de TDD do item
  5.5. Nao decidi nada sobre a pendencia de re-autenticacao do item 5.4 -
  continua em aberto para quando a etapa for retomada.

## 9. Criterio de pronto

- [ ] Os 8 testes do item 5.5 passam - saida real no diario
- [ ] Existe teste de IDOR e ele passa
- [ ] Recurso de outra instituicao responde 404, verificado
- [ ] Mixin destrutivo grava auditoria - conferido no banco, nao presumido
- [ ] Matriz do item 4 refletida em codigo
- [ ] Um arquivo por permissao, nenhum passa de 300 linhas
- [ ] Recomendacao sobre re-autenticacao registrada
- [ ] `IA.md` atualizado com o padrao de acao destrutiva
- [ ] Commit feito, so com arquivos desta etapa
