# E05 - Creditos (ledger)

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
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

_(vazio - primeira entrada e sua)_

## 9. Criterio de pronto

- [ ] Os 12 testes do item 5.8 passam - saida real no diario
- [ ] O teste de concorrencia e **realmente** concorrente
- [ ] Imutabilidade garantida por excecao, nao por convencao
- [ ] Nenhum `float` na cadeia de credito - verificado
- [ ] Idempotencia provada com retry simulado
- [ ] Reducao de alocacao grava auditoria - conferido no banco
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] `IA.md` atualizado com a regra de bloqueio implementada
- [ ] Commit feito, so com arquivos desta etapa
