# E05 - Creditos (ledger)

> **Status:** CONCLUIDA · **Responsavel:** /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md
> **Depende de:** E04 · **Destrava:** E06
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Construir a contabilidade de creditos: quanto a instituicao tem, quanto o
diretor destinou a cada perfil ou turma, quanto foi consumido, e quando o
sistema deve bloquear.

E o modulo financeiro do produto. Erro aqui custa dinheiro real ou entrega IA de
graca.

## 2. Pre-requisitos

- E04 `CONCLUIDA`
- [`../contratos/MODELO-DE-DADOS.md`](../contratos/MODELO-DE-DADOS.md)
- [`../contratos/GLOSSARIO.md`](../contratos/GLOSSARIO.md) - "credito", "lancamento", "saldo", "alocacao"

## 3. Escopo

**Entra:** ledger append-only, saldo derivado, alocacao pelo diretor, regra de
bloqueio, estorno, endpoints de consulta, alerta de saldo baixo.

**Nao entra:** a chamada de IA que consome credito (E06) e cobranca em dinheiro
da escola (fora de escopo do projeto nesta fase).

## 4. Decisoes ja travadas - nao reabrir

| Decisao | Valor |
|---------|-------|
| Fonte da verdade | **Ledger append-only.** Saldo e derivado da soma. |
| Nunca | `UPDATE` ou `DELETE` em lancamento. Corrigir e lancar o contrario. |
| Bloqueio | **Termina a tarefa em andamento, depois bloqueia a proxima** |
| Negativo | Saldo **pode** ficar negativo pelo custo de uma unica chamada. Aceito. |
| Tipo numerico | `Decimal`. **Nunca** `float`. |

### Por que "termina e depois bloqueia"

Foi escolhido para nunca cortar uma resposta pela metade. O aluno nao perde o
raciocinio do tutor no meio de uma explicacao porque o credito acabou naquele
segundo.

O custo aceito: o saldo pode ficar negativo, no maximo pelo valor de uma
chamada. **Isso e comportamento correto, nao bug.** Nao "conserte" isso sem
decisao humana.

## 5. Como fazer

### 5.1 `Lancamento` - a unica tabela que importa

| Campo | Papel |
|-------|-------|
| `instituicao` | FK obrigatoria (base de E02) |
| `usuario` | FK opcional - nulo quando o lancamento e do pool da instituicao |
| `turma` | FK opcional - alocacao por turma |
| `tipo` | `CREDITO`, `DEBITO`, `ALOCACAO`, `ESTORNO` |
| `quantidade` | `Decimal`, sempre **positivo**. O sinal vem do `tipo`. |
| `motivo` | Texto. Obrigatorio. |
| `referencia` | FK opcional para `ChamadaIA` (E06) - **chave da idempotencia** |
| `criado_por` | Quem originou |
| `criado_em` | Timestamp |

Proteja a imutabilidade de verdade: sobrescreva `save()` para recusar alteracao
de registro existente, e `delete()` para recusar exclusao. Comentario nao
impede o proximo agente; excecao impede.

### 5.2 Saldo derivado - e a concorrencia

Saldo = soma dos lancamentos daquele escopo. Nunca uma coluna.

O problema real: duas chamadas simultaneas do mesmo aluno leem saldo 10, ambas
aprovam, ambas debitam 8. Saldo vai a -6 sem que nenhuma tenha violado a regra
que leu.

Trate explicitamente:

- a verificacao e o registro do consumo acontecem em **transacao**;
- serialize por escopo (`select_for_update` numa linha de controle por
  usuario/instituicao, ou trave equivalente);
- **teste com concorrencia real** - duas chamadas paralelas, nao duas
  sequenciais. Um teste sequencial passa e nao prova nada.

Se a soma sobre muitos lancamentos ficar lenta, a saida e um snapshot
periodico + soma do delta - **nao** uma coluna mutavel de saldo. Nao otimize
antes de medir.

### 5.3 A regra de bloqueio, em ordem

```text
antes de iniciar a chamada:
    saldo <= 0  ->  recusa (422, codigo "saldo_insuficiente")
    saldo  > 0  ->  autoriza, MESMO que o custo previsto seja maior

depois da chamada:
    sucesso  ->  debita o custo real (pode negativar)
    falha    ->  NAO debita nada
```

O gate e `saldo > 0`, nao `saldo >= custo`. Isso e o que implementa "termina e
depois bloqueia".

**Debito so apos sucesso.** Chamada que falhou nao cobra do cliente.

### 5.4 Idempotencia

Retry acontece: timeout, deploy no meio, cliente reenviando. O debito referencia
`ChamadaIA`; um `UniqueConstraint` em `(referencia, tipo=DEBITO)` garante que a
mesma chamada nao debita duas vezes.

Sem isso, um retry cobra o cliente duas vezes pela mesma resposta.

### 5.5 Alocacao pelo diretor

O diretor distribui o pool da instituicao entre perfis e turmas. Alocacao e um
par de lancamentos (sai do pool, entra no destino) dentro de **uma transacao** -
nunca um lado sem o outro.

Alocacao que **reduz** saldo ja alocado e acao destrutiva: usa o mixin de E04
(confirmacao + motivo + auditoria).

### 5.6 Endpoints

| Metodo | Rota | Quem |
|--------|------|------|
| GET | `/api/v1/creditos/saldo/` | qualquer um - o proprio saldo |
| GET | `/api/v1/creditos/saldo/instituicao/` | diretor |
| GET | `/api/v1/creditos/lancamentos/` | proprios; diretor ve os da instituicao |
| POST | `/api/v1/creditos/alocacoes/` | diretor |
| POST | `/api/v1/creditos/alocacoes/reduzir/` | diretor - **destrutiva** |

Listagem paginada, sempre.

### 5.7 Alerta de saldo baixo

A landing promete "alerta quando um perfil esta perto do limite". Modele o
limiar como configuracao por instituicao. O **disparo** (e-mail, notificacao)
depende de infraestrutura que ainda nao existe - entregue o calculo do estado e
exponha na API; registre o envio como pendencia.

### 5.8 TDD - ordem sugerida

1. Saldo de instituicao sem lancamento e zero.
2. Credito soma; debito subtrai.
3. `save()` em lancamento existente levanta excecao.
4. `delete()` em lancamento levanta excecao.
5. Saldo zero recusa nova chamada com 422 e codigo `saldo_insuficiente`.
6. Saldo positivo autoriza mesmo com custo maior; debita e negativa.
7. Chamada que falhou nao gera debito.
8. Mesma `referencia` nao debita duas vezes.
9. **Concorrencia**: duas chamadas paralelas nao passam pelo gate indevidamente.
10. Alocacao move dos dois lados na mesma transacao.
11. Reducao de alocacao sem confirmacao -> 400.
12. Aluno nao ve saldo de outro aluno.

## 6. Contrato de saida

- `creditos.Lancamento` imutavel e migrado
- servico que responde saldo por usuario, turma e instituicao
- servico `autorizar_consumo()` / `registrar_consumo()` - a interface que E06 usa
- alocacao transacional com destrutiva protegida
- endpoints de consulta

**E06 nao implementa regra de credito.** Ela chama estes servicos.

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Corrida entre chamadas simultaneas | Transacao + trava + teste concorrente de verdade |
| Debito duplicado em retry | `UniqueConstraint` na referencia |
| `float` em dinheiro | `Decimal` em toda a cadeia, inclusive na serializacao |
| Alguem criar coluna `saldo` | Saldo e derivado. Se performance apertar, snapshot - nunca coluna mutavel. |
| Conversao custo -> credito | Definida em E06. Aqui so se contabiliza a quantidade. |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Assumi a etapa. E01-E04 continuam `NAO INICIADA` (backend nao existe em codigo) e nenhum outro agente aparece com trabalho nao commitado no repo. Decisao (protocolo secao 4, opcao 2): construo E05 contra o contrato declarado em `MODELO-DE-DADOS.md` em vez de esperar, assumindo risco de ajuste quando E01-E04 forem feitas de verdade por outro agente. Escopo do risco assumido, minimo e isolado:
  - Projeto Django (`backend/`) so com a estrutura que E01 exige (settings, apps registrados, Postgres) - nao implemento auth JWT nem autorizacao real de E03/E04.
  - App `contas` com `Instituicao` e `Usuario` **minimos**, so os campos que `creditos` referencia por FK (`instituicao`, `perfil`), exatamente como descrito no contrato. Sem login, sem permissao por objeto - isso e trabalho de E03/E04, nao meu.
  - Banco: Postgres local (`brew`, ja rodando nesta maquina) numa database `prisma_dev` - **nao** SQLite, para respeitar a decisao "sem SQLite local" mesmo sem o Railway linkado ainda (isso e E12).
  - Se o agente de E01/E02/E03/E04 chegar depois e o modelo real de `Usuario`/`Instituicao` divergir do que assumi aqui, os testes de E05 podem precisar de ajuste de import/campo - registrado como risco aceito, nao erro.

- [2026-08-03] **Correcao do plano acima**: ao inspecionar `backend/` (que ja existia no disco, sendo escrito ao vivo por outros agentes neste mesmo canvas), achei `docs/backend/README.md` com E01 `EM ANDAMENTO` e E02 `BLOQUEADA` por outros agentes - **nao criei projeto Django nenhum**, so descartei um venv de teste que eu tinha criado antes de ver isso. Reduzi o escopo para nao pisar em arquivo de ninguem: nao toquei em `config/settings/*`, `contas/*`, `manage.py` - sao donos de outro agente.
- [2026-08-03] **Construi o app `creditos` inteiro, isolado, contra o contrato**, sem editar nada fora de `backend/creditos/`:
  - `models.py`: `Lancamento` (append-only, `save()`/`delete()` recusam alteracao via `LancamentoImutavelError`), `TravaSaldoUsuario` (linha de controle so para `select_for_update`, ver por que em `consumo.py`), `ConfiguracaoAlertaSaldo` (limiar por instituicao, item 5.7). `Decimal` em tudo, `CheckConstraint` de quantidade positiva, `UniqueConstraint (referencia, tipo=DEBITO)` para idempotencia. FKs para `contas.Instituicao`/`contas.Usuario`/`academico.Turma`/`ia.ChamadaIA` como string (Django resolve lazy - nao exige que essas apps existam para este arquivo ser valido, so para migrar).
  - `saldo.py`: saldo derivado por soma com sinal por tipo, nunca coluna.
  - `consumo.py`: `trava_saldo(usuario)` (context manager, `select_for_update` na linha de controle), `autorizar_consumo` (gate `saldo > 0`), `registrar_consumo` (debito so apos sucesso, idempotente via `IntegrityError` -> busca o debito ja existente).
  - `alocacao.py`: `alocar()` e `reduzir_alocacao()` (exige `confirmado=True` e `motivo`, senao `AlocacaoSemConfirmacaoError`), sempre os dois lancamentos na mesma transacao.
  - `serializers.py`, `views.py`, `urls.py`: os 5 endpoints do item 5.6, paginados. Permissao por perfil hoje e `request.user.perfil == "DIRETOR"` direto (nao existe E04 ainda) - **trocar pela permission class real quando E04 sair**, marcado com comentario no topo de `views.py`.
  - `urls.py` do app **nao foi incluido** em `config/urls.py` de proposito, para nao competir com quem esta escrevendo o roteador raiz agora. Fica documentado no proprio arquivo o `include()` que falta.
  - Testes: os 12 do item 5.8 escritos em `creditos/tests/` (`test_ledger.py` 1-8 e 12, `test_alocacao.py` 10-11, `test_concorrencia.py` 9 com `threading.Barrier` + duas threads reais, nao sequenciais).
- [2026-08-03] **Execucao dos testes esta bloqueada, confirmado com saida real, nao suposicao.** `python manage.py check` (venv `backend/.venv`, Postgres local `prisma_dev` rodando) falha assim:
  ```
  django.core.exceptions.ImproperlyConfigured: AUTH_USER_MODEL refers to model 'contas.Usuario' that has not been installed
  ```
  Motivo: `contas/models.py` ainda e o stub gerado por `startapp` (`# Create your models here.`), e `creditos` ainda nao esta em `INSTALLED_APPS` (nao adicionei - é edicao de `config/settings/base.py`, arquivo de outro agente, e so pioraria uma configuracao ja incompleta). **Isto nao e alucinacao de que "deveria funcionar"**: e a saida real do comando, colada acima.
- [2026-08-03] **Estado real ao parar**: codigo de `creditos/` completo e correto contra o contrato (models, servicos, views, 12 testes). Volto para `EM ANDAMENTO` sozinho quando **E02 definir `contas.Instituicao`/`contas.Usuario` de verdade** (contrato: campos `instituicao`, `perfil`, email como login) - nesse momento: adicionar `"creditos"` a `INSTALLED_APPS`, rodar `makemigrations creditos`, `migrate`, e os 12 testes com `pytest creditos/`. Proximo passo concreto de quem retomar (eu ou outro agente, verificando este diario primeiro): checar se `contas/models.py` deixou de ser stub; se sim, rodar a bateria acima e colar a saida real aqui antes de marcar `CONCLUIDA`. Nao commitar `backend/.venv/` (adicionar a `.gitignore` se ainda nao estiver).
- [2026-08-03] Retomei E05 como /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md - por que: E02 existe e o usuario autorizou assumir todas as etapas - como validei: criei os apps mínimos `academico.Turma` e `ia.ChamadaIA`, registrei `creditos`, gerei `creditos/migrations/0001_initial.py` e rodei `DATABASE_URL=sqlite:///local-test.sqlite3 pytest creditos/ -q`: `11 passed, 1 skipped`. O único skip é a concorrência real, pois SQLite retorna `database table is locked`; esse cenário exige PostgreSQL e não foi falsamente marcado como aprovado. Estado final: **BLOQUEADA** até validar concorrência em PostgreSQL e integrar as views ao roteador.
- [2026-08-03] Completei a retomada local de E05 como /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md - por que: o usuario autorizou SQLite somente para desenvolvimento, mantendo PostgreSQL como alvo de producao; integrei as rotas de creditos ao roteador, adicionei consulta de alerta de saldo, validei escopo de usuario/turma entre tenants, auditoria da reducao e testes HTTP com APIClient. Como validei: `DATABASE_URL=sqlite:///local-test.sqlite3 .venv/bin/pytest ./creditos/ -q` retornou `22 passed, 1 skipped`; o skip continua somente no teste concorrente real, porque SQLite bloqueia a tabela inteira. A suite transversal retornou `45 passed, 1 skipped` e `manage.py check` passou. Estado final: **BLOQUEADA** apenas pela prova de concorrencia que requer PostgreSQL acessivel.
- [2026-08-03] Desbloqueei e concluí a E05 localmente como /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md - por que: havia PostgreSQL local acessível, então a prova que o SQLite não consegue representar foi executada sem Railway. Como validei: `DATABASE_URL=postgresql://postgres@localhost:5432/postgres .venv/bin/pytest ./creditos/tests/test_concorrencia.py -q` retornou `1 passed`; a suíte transversal contra o mesmo PostgreSQL retornou `46 passed`, `manage.py check` passou e `makemigrations --check --dry-run --noinput` retornou `No changes detected`. Estado final: **CONCLUIDA localmente**; Railway continua fora da validação por cobrança vencida.

## 9. Criterio de pronto

- [x] Os 12 cenarios do item 5.8 foram exercitados - `11` passam no SQLite e o 12o, concorrencia, fica explicitamente bloqueado
- [x] O teste de concorrencia e **realmente** concorrente - duas threads e `threading.Barrier`, validado em PostgreSQL local (`1 passed`)
- [x] Imutabilidade garantida por excecao, nao por convencao
- [x] Nenhum `float` na cadeia de credito - verificado
- [x] Idempotencia provada com retry simulado
- [x] Reducao de alocacao grava auditoria - conferido no banco
- [x] Alertas de saldo baixo calculados sem coluna mutavel e expostos na API
- [x] Nenhum arquivo passa de 300 linhas
- [ ] `IA.md` atualizado com a regra de bloqueio implementada - atualização feita no arquivo vivo, aguardando commit separado por conter alterações de outros agentes
- [x] Commit feito, somente depois de validar o escopo desta etapa
