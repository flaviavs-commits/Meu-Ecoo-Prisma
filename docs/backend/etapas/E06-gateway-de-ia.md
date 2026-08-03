# E06 - Gateway de IA (interface)

> **Status:** BLOQUEADA · **Responsavel:** Claude (sessao canvas E06)
> **Depende de:** E05 · **Destrava:** E07
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Construir o **unico caminho** pelo qual o sistema fala com IA: a camada que
autoriza credito, escolhe o modelo, chama o provedor, contabiliza custo e
registra o uso.

**Sem chamada real ao OpenRouter nesta etapa.** Isso e decisao explicita de
escopo. O que se entrega e a estrutura completa e testada, com um provedor falso
no lugar do real.

## 2. Pre-requisitos

- E05 `CONCLUIDA` (servicos de credito disponiveis)
- [`../contratos/LGPD-E-DADOS-SENSIVEIS.md`](../contratos/LGPD-E-DADOS-SENSIVEIS.md) - item 4
- [`../FERRAMENTAS-E-ECOSSISTEMA.md`](../FERRAMENTAS-E-ECOSSISTEMA.md)

## 3. Escopo

**Entra:** interface de provedor, provedor falso, registro de `ChamadaIA`,
tabela de conversao custo -> credito, roteamento por classe de tarefa,
integracao com o ledger, tratamento de falha.

**Nao entra:** chave real do OpenRouter, chamada de rede de verdade, e a
integracao com os repositorios satelites (isso e [E13](E13-api-nos-repos-satelites.md),
em outros repositorios).

## 4. Decisoes ja travadas - nao reabrir

| Decisao | Valor |
|---------|-------|
| Provedor | OpenRouter, como motor unico - **mas nao chamado nesta etapa** |
| Gateway | Toda chamada de IA passa pelo backend. O frontend **nunca** fala com o OpenRouter. |
| Chave | Server-side, em variavel de ambiente. Nunca no repositorio, nunca no frontend. |
| Roteamento | Classe de tarefa -> modelo, em **configuracao**, nao em codigo |
| Credito | Unidade interna, por tabela de conversao com margem |
| Debito | So apos resposta bem-sucedida |

## 5. Como fazer

### 5.1 A interface de provedor

O sistema nunca depende do formato cru do OpenRouter. Uma interface propria, com
duas implementacoes:

```text
ia/provedores/
├── base.py             # a interface (ABC)
├── falso.py            # resposta deterministica, para teste e para esta fase
└── openrouter.py       # esqueleto - NAO chama a rede nesta etapa
```

A interface recebe um pedido do dominio e devolve um resultado do dominio -
texto, tokens de entrada e saida, modelo usado, custo bruto. Se um campo do
OpenRouter vazar para fora de `openrouter.py`, a abstracao falhou.

`falso.py` nao e codigo descartavel: e o que permite testar todo o resto sem
gastar dinheiro nem depender de rede. Trate com o mesmo cuidado do resto.

Selecao por configuracao (`IA_PROVEDOR=falso|openrouter`), com **`falso` como
padrao** enquanto a integracao real nao for aprovada.

### 5.2 Classe de tarefa -> modelo

Classes: `TUTORIA`, `GERACAO`, `CORRECAO`, `RESUMO`.

O mapa classe -> modelo vive em **configuracao**, nunca espalhado em `if`.
Trocar o modelo de resumo para um mais barato tem que ser mudanca de
configuracao, nao de codigo.

### 5.3 Custo -> credito

Tabela configuravel, com margem. O custo do provedor vem em dolar por token; o
credito e a unidade interna que o cliente enxerga.

- conversao em **um** lugar, testada isoladamente;
- `Decimal` em toda a cadeia;
- arredondamento **explicito e sempre a favor do sistema** (nunca cobrar menos
  do que custou por erro de arredondamento);
- a margem e configuracao, nao constante no meio do codigo.

### 5.4 `ChamadaIA`

| Campo | Papel |
|-------|-------|
| `instituicao`, `usuario` | Quem consumiu |
| `classe_tarefa` | O que foi pedido |
| `modelo` | Quem respondeu de fato |
| `tokens_entrada` / `tokens_saida` | Medida bruta |
| `custo_bruto` | O que o provedor cobrou (`Decimal`) |
| `creditos_debitados` | O que o cliente pagou |
| `status` | `PENDENTE`, `SUCESSO`, `ERRO` |
| `erro_codigo` | Quando falha |
| `criado_em`, `concluido_em` | Duracao |

**Nunca guarde aqui o conteudo do prompt nem da resposta.** Isso e conversa de
aluno e vive em `memoria` (E07), com regra propria de acesso. Misturar os dois
transformaria a tabela de contabilidade em deposito de dado sensivel.

### 5.5 O fluxo completo

```text
1. cria ChamadaIA (PENDENTE)
2. pergunta ao ledger: pode consumir?  (saldo > 0)
      nao -> 422 saldo_insuficiente, chamada vira ERRO, nada e debitado
3. resolve classe de tarefa -> modelo
4. chama o provedor
      erro -> chamada vira ERRO, NADA e debitado
5. converte custo -> creditos
6. registra o debito no ledger, referenciando esta ChamadaIA
7. chamada vira SUCESSO
```

Os passos 5-7 acontecem em **uma transacao**: nao pode existir chamada com
sucesso sem debito, nem debito sem chamada.

O gate e `saldo > 0`, nao `saldo >= custo previsto` - e o que implementa
"termina e depois bloqueia" (E05). Nao "melhore" isso.

### 5.6 Falha do provedor

Falha externa e certeza, nao possibilidade. Trate:

- **timeout explicito** - nunca chamada de rede sem limite de tempo;
- retry so em erro transitorio (429, 5xx), com espera crescente e teto baixo;
- retry **nunca** duplica debito - a idempotencia por `referencia` de E05 e o
  que garante isso;
- erro do provedor **nunca** vaza cru para o cliente: vira codigo do
  [contrato de API](../contratos/API-CONVENCOES.md);
- log registra a falha com id da chamada, **sem** o conteudo.

### 5.7 Privacidade - o ponto de saida do sistema

Este gateway e o unico lugar por onde conteudo de aluno - possivelmente menor de
idade - sai para um terceiro.

- registre **que** houve envio (metrica, tokens), nunca **o que** foi enviado;
- nada de prompt em log, telemetria ou mensagem de erro;
- quando a integracao real chegar, verifique politica de retencao do provedor.
  Registre isso como pendencia agora.

### 5.8 TDD - ordem sugerida

1. Provedor falso devolve resposta deterministica.
2. Chamada com saldo zero -> 422, nenhum debito, chamada `ERRO`.
3. Chamada com saldo positivo -> `SUCESSO` e debito registrado.
4. Falha do provedor -> `ERRO`, nenhum debito.
5. Conversao custo -> credito confere, inclusive no arredondamento.
6. Classe de tarefa resolve o modelo configurado.
7. Retry da mesma chamada nao debita duas vezes.
8. Nenhum conteudo de prompt aparece em `ChamadaIA` nem em log.
9. Trocar `IA_PROVEDOR` troca a implementacao sem tocar no dominio.

## 6. Contrato de saida

- servico unico de chamada de IA - a **unica** porta de saida para IA
- interface de provedor com implementacao falsa funcionando
- `ia.ChamadaIA` migrado
- conversao custo -> credito isolada e testada
- integracao com o ledger de E05, transacional e idempotente
- `openrouter.py` como esqueleto documentado, desligado por padrao

E07 e as demais features de IA chamam **este servico**. Nenhuma outra parte do
sistema fala com provedor de IA.

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Chave real vazar | Nunca no repositorio; `.env.example` so com o nome |
| Prompt de aluno em log | Proibido por design; teste que verifica |
| Chamada sem timeout trava worker | Timeout obrigatorio |
| Retry duplicando debito | Idempotencia por `referencia` (E05) |
| Detalhe do OpenRouter vazar para o dominio | Fica confinado em `openrouter.py` |
| Retencao de dado pelo provedor | **Pendencia aberta** - verificar antes de ligar a integracao real |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Peguei E06 para iniciar o MVP e verifiquei o pre-requisito - a
  pasta `backend/` **nao existe** no repositorio ainda; E01, E02, E03, E04 e
  E05 seguem `NAO INICIADA` no `README.md` (nenhum tem responsavel nem
  trabalho registrado). Nao existe projeto Django, nao existe app `creditos`
  com ledger, nao existe `Usuario`/`Instituicao`. A interface de provedor e o
  provedor falso de E06 nao dependem so de codigo de dominio: dependem do
  projeto Django existir (E01), do modelo `Instituicao`/`Usuario` (E02), e
  principalmente do servico de ledger de E05 para o gate `saldo > 0` e para o
  debito transacional (secao 5.5 desta etapa). Construir isso agora seria
  implementar E01-E05 "de passagem", que o protocolo proibe explicitamente
  (`PROTOCOLO-DO-AGENTE.md`, secao 4: "Nao implemente a etapa dos outros de
  passagem para se desbloquear") - alem de arriscar colidir com outro agente
  que esteja com essas etapas abertas sem ainda ter comitado.
  - Decisao: marcar esta etapa como `BLOQUEADA` em vez de simular progresso.
  - O que destrava: E01 concluida (projeto Django + `backend/` criado) e E05
    concluida (ledger com `pode_consumir`/debito transacional e idempotencia
    por `referencia`). Assim que qualquer uma delas avancar, revisitar aqui.
  - Enquanto isso, deixei pronta a leitura completa da etapa (contrato de
    saida, criterio de pronto, riscos) para que a implementacao comece
    imediatamente quando a dependencia cair - nenhum design novo foi
    necessario, o desenho da secao 5 ja cobre a interface de provedor, o mapa
    classe->modelo, a conversao custo->credito e o fluxo transacional com o
    ledger.
  - Nao commitei nada alem desta atualizacao de status/diario nesta etapa.

## 9. Criterio de pronto

- [ ] Os 9 testes do item 5.8 passam - saida real no diario
- [ ] Nenhuma chamada de rede real acontece na suite de testes
- [ ] `IA_PROVEDOR` padrao e `falso`
- [ ] Nenhum conteudo de prompt/resposta em `ChamadaIA` ou log - verificado
- [ ] Mapa classe -> modelo esta em configuracao, nao em codigo
- [ ] Debito so ocorre em sucesso - testado nos dois caminhos
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] Pendencia de retencao do provedor registrada
- [ ] `IA.md` atualizado com o desenho do gateway
- [ ] Commit feito, so com arquivos desta etapa
