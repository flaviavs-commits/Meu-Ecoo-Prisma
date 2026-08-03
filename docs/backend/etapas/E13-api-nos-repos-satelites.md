# E13 - API HTTP nos repositorios satelites

> **Status:** AGUARDANDO DECISAO · **Responsavel:** Claude (sessao 2026-08-03)
> **Depende de:** nada neste repositorio · **Destrava:** a integracao real de E06
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. ⚠️ Esta etapa acontece em OUTROS repositorios

O trabalho de codigo desta etapa **nao e feito em `Meu-Ecoo-Prisma`**. Ele
acontece em:

- `flaviavs-commits/Estudo-IA-Resumo` (privado)
- `Felipe-Alcantara/Audiofy-Content-AI` (publico)

Este arquivo e o **contrato e o diario** da frente de trabalho. O codigo vive
la; a decisao e o registro ficam aqui, para o backend do Prisma saber contra o
que programar.

Cada um daqueles repositorios tem o proprio `IA.md`, o proprio README e o
proprio padrao. **Respeite o padrao de la**, nao imponha o daqui.

## 2. Objetivo

Transformar duas ferramentas de linha de comando em servicos HTTP que o backend
do Prisma possa chamar.

## 3. O estado real hoje

Verificado em 2026-08-01. **Reconfirme antes de comecar** - os dois estao em
evolucao.

| Repositorio | O que existe | O que falta |
|------------|--------------|-------------|
| `Estudo-IA-Resumo` | CLI em Python. `resumo-ia/app/api/cli.py` - a pasta chama "api" mas e linha de comando. Estrutura ja separada em `services/`, `integrations/`, `domain/`, com testes. | Camada HTTP. Nenhuma dependencia de servidor web. |
| `Audiofy-Content-AI` | MVP maduro com app Electron. `src/audiofy/bridge.py` e uma ponte JSON por stdout, com comandos bem definidos. | Camada HTTP. Nenhuma dependencia de servidor web. |

A boa noticia: os dois ja separam dominio de interface. `bridge.py` inclusive ja
tem um contrato de comandos - virar HTTP e envolver, nao reescrever.

## 4. Escopo

**Entra:** camada HTTP fina sobre a logica existente, autenticacao entre
servicos, contrato de request/response, tratamento de erro, documentacao.

**Nao entra:** reescrever a logica de negocio daqueles projetos. Se a API exigir
mudar o nucleo, **pare e pergunte** - talvez o contrato e que esteja errado.

## 5. Como fazer

### 5.1 Camada fina, nunca regra nova

A API expoe o que ja existe. Nenhuma regra de negocio nova nasce na camada HTTP.

`bridge.py` ja e praticamente essa camada, em outro transporte: os comandos sao
o vocabulario da API. Aproveite.

### 5.2 Operacao demorada nao cabe em request sincrono

Gerar audio de um episodio leva minutos. Um `POST` que so responde no fim vai
dar timeout em qualquer proxy.

Padrao recomendado - **trabalho assincrono com consulta de status**:

```
POST /jobs/           -> 202 Accepted, { "job_id": "..." }
GET  /jobs/<id>/      -> { "status": "processando|concluido|erro", ... }
GET  /jobs/<id>/saida -> o resultado, quando concluido
```

Para `Estudo-IA-Resumo`, resumo de texto curto pode ser sincrono. **Meça antes
de decidir** e registre o tempo observado - nao escolha por intuicao.

Isso e uma decisao de arquitetura com consequencia no Prisma: sincrono e
assincrono geram integracoes diferentes em E06. Registre a escolha aqui.

**Decisao registrada (2026-08-03):**

- `Estudo-IA-Resumo`: **assincrono (`POST /jobs`) para tudo**, apesar de
  texto curto poder ser rapido. Motivo: a mesma rota tambem aceita audio
  (Whisper local, minutos), imagem, PDF e URL - variando o tempo de resposta
  por tipo de entrada obrigaria E06 a tratar dois contratos para o mesmo
  endpoint. Um unico padrao assincrono e mais simples de integrar e nao tem
  timeout escondido. Tempo sera medido e registrado aqui quando os testes do
  item 5.8 rodarem (endpoint `POST /jobs` -> 202 mede o tempo de entrada na
  fila, nao o de processamento).
- `Audiofy-Content-AI`: **assincrono**, ja e o padrao do `bridge.py`
  (`generate` + `status`). A API HTTP so expoe o que ja existe.

### 5.3 Autenticacao entre servicos

Nao e usuario final chamando: e o backend do Prisma.

- token de servico em cabecalho, guardado em variavel de ambiente dos dois
  lados;
- **nunca** exponha a API na internet sem autenticacao - ela gasta credito de IA
  de verdade;
- rate limit, para um bug no Prisma nao torrar a conta do OpenRouter;
- se possivel, restrinja a origem.

### 5.4-pre Reconfirmacao do estado (2026-08-03)

Clonados os dois repositorios via `gh repo clone` para leitura direta:

- `Estudo-IA-Resumo`: confirmado como no item 3. `app/api/cli.py` (Typer) e
  camada fina sobre `app/services/resumo_service.py`. `openrouter_client.py`
  **descarta** o campo `usage` da resposta da OpenRouter - hoje nao ha custo
  disponivel para expor. OpenRouter aceita `"usage": {"include": true}` no
  payload para devolver `usage.cost`; captar isso e extensao minima e
  necessaria para cumprir o item 5.4 (custo obrigatorio), nao regra de
  negocio nova.
- `Audiofy-Content-AI`: `bridge.py` **ja implementa o padrao assincrono**
  pedido no item 5.2 - `generate` inicia um worker destacado
  (`launch_detached`) e retorna imediatamente; `status`/`status <item-id>`
  consulta o estado (`pendente/rodando/concluido/erro` via
  `GenerationTracker`); custo real ja e rastreado em
  `_episode_summary` (`cost_usd`, `cost_exact`). A API HTTP aqui e
  essencialmente mapear comandos existentes do bridge para rotas - baixo
  risco de mexer no nucleo.

### 5.4 Contrato

Definido **aqui** antes de existir codigo, para que E06 possa programar contra
ele em paralelo:

| Item | Regra |
|------|-------|
| Formato | JSON nos dois sentidos |
| Erro | `{ "erro": { "codigo": ..., "mensagem": ... } }`, igual ao [contrato do Prisma](../contratos/API-CONVENCOES.md) |
| Custo | A resposta informa o custo real da operacao - o Prisma precisa disso para debitar credito |
| Idempotencia | Aceitar uma chave de idempotencia; o mesmo pedido nao processa duas vezes |
| Timeout | Documentado e conhecido pelos dois lados |

**Custo e idempotencia nao sao opcionais.** Sem custo, o ledger de E05 nao tem o
que debitar. Sem idempotencia, um retry cobra o cliente duas vezes.

### 5.5 Quem paga a IA

Aqueles projetos ja chamam o OpenRouter com chave propria. Se forem chamados
pelo Prisma, **quem paga?**

Duas topologias, e a escolha muda o desenho:

| Opcao | Consequencia |
|-------|--------------|
| O satelite usa a propria chave | Simples. Mas o custo fica fora do ledger do Prisma - o cliente consome IA sem debitar credito. |
| O satelite recebe a chave/orcamento do Prisma | Mantem o gateway como ponto unico de contabilidade, como o desenho manda. Mais trabalho. |

**Nao decida sozinho.** Registre a recomendacao (a segunda opcao preserva o
principio de gateway unico) e marque `AGUARDANDO DECISAO`.

**Recomendacao registrada (2026-08-03), aguardando decisao humana:** opcao 2
(satelite recebe chave/orcamento do Prisma). Para nao bloquear o MVP tecnico
enquanto se decide, a implementacao inicial usa a chave propria de cada
satelite (opcao 1) **por tras de uma variavel de ambiente separada e clara**
(`RESUMO_IA_OPENROUTER_API_KEY` / a chave ja existente do Audiofy), para que
trocar para "chave vinda do Prisma" no futuro seja so mudar de onde a
variavel e alimentada, sem tocar no formato do contrato HTTP. O campo
`custo_usd` na resposta ja existe independente dessa escolha, entao o ledger
de E05 pode ser ligado assim que a decisao 5.5 sair.

### 5.6 Onde roda

Provavelmente Railway, como o resto. Vale para os dois:

- servico proprio, nao dentro do backend do Prisma;
- variaveis de ambiente separadas;
- **projeto Railway novo tem custo** - pergunte antes de criar.

### 5.7 Privacidade

Se o Prisma enviar conteudo de aluno para essas APIs, dado pessoal de menor
passa a trafegar entre servicos. Vale o
[contrato de LGPD](../contratos/LGPD-E-DADOS-SENSIVEIS.md):

- so o necessario trafega;
- nada de conteudo em log;
- retencao definida - o satelite guarda o texto enviado? Por quanto tempo?
  **Responda isso explicitamente.**

### 5.8 TDD - ordem sugerida

Nos repositorios de destino, seguindo o padrao de teste de cada um:

1. Endpoint sem token -> 401.
2. Pedido valido -> 202 com identificador de job.
3. Consulta de status devolve o estado real.
4. Job concluido devolve a saida.
5. Falha interna -> erro no formato do contrato, sem stack trace.
6. Mesma chave de idempotencia nao processa duas vezes.
7. Resposta informa o custo real.
8. Rate limit responde 429.

## 6. Contrato de saida

- os dois repositorios expondo API HTTP autenticada
- contrato documentado **aqui**, para E06 programar contra ele
- decisao sobre sincrono vs. assincrono registrada
- decisao sobre quem paga a IA registrada
- endereco e forma de autenticacao comunicados a quem cuida de E06

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| API aberta gastando credito de IA | Token de servico + rate limit |
| Timeout em operacao longa | Job assincrono. Meça antes de decidir. |
| Custo invisivel ao ledger do Prisma | Resposta informa custo. Item 5.5 pendente de decisao. |
| Retry cobrando duas vezes | Chave de idempotencia |
| Impor o padrao do Prisma a outro repo | Respeite o padrao de la |
| Mudar o nucleo daqueles projetos | Se precisar, pare e pergunte |
| Dado de menor trafegando entre servicos | Minimizacao + retencao definida |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Registre aqui **tambem** o que voce fizer nos outros repositorios: qual repo,
> qual commit, qual decisao. Este arquivo e o ponto de encontro das duas frentes.
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Peguei a etapa, status para EM ANDAMENTO, assinei - reconfirmando o estado dos dois repositorios satelites antes de desenhar a API, conforme item 3 pede ("reconfirme antes de comecar") - validando via `gh repo view` e clone dos dois repos para leitura direta do codigo atual.
- [2026-08-03] Suspendi a implementacao nesta sessao - o escopo do usuario agora e continuar localmente no Meu-Ecoo-Prisma, enquanto E13 exige alteracoes e commits em dois repositorios externos; sem decisao de contrato de custo/retencao e sem coordenacao dos responsaveis daqueles repositorios, nao alterei codigo fora deste repositorio. O contrato e as decisoes ja registradas permanecem disponiveis para retomada segura.

## 9. Criterio de pronto

- [ ] Estado atual dos dois repositorios reconfirmado antes de comecar
- [ ] Os 8 testes do item 5.8 passam em cada repositorio - saida real no diario
- [ ] Contrato documentado neste arquivo, suficiente para E06 programar contra ele
- [ ] Decisao sincrono vs. assincrono registrada, com tempo medido
- [ ] Decisao sobre quem paga a IA registrada (ou pendencia explicita)
- [ ] Nenhum segredo em repositorio - inclusive no publico
- [ ] `IA.md` de **cada** repositorio de destino atualizado, conforme o padrao de la
- [ ] Retencao de dado pelos satelites respondida
- [ ] Commits feitos nos repositorios de destino, referenciados aqui
