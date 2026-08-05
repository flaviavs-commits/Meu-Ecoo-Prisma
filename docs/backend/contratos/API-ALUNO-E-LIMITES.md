# Contrato — API do aluno e limite percentual

**Status:** vigente para o backend local
**Responsável:** Code Review
**Base:** Django REST Framework, prefixo `/api/v1/`

Todas as rotas abaixo exigem autenticação JWT. O backend deriva o usuário do
token; IDs enviados pelo cliente não substituem as verificações de tenant e de
proprietário.

## Limites e planos

| Método e rota | Permissão | Resultado |
|---|---|---|
| `GET /limites/uso/` | conta autenticada | limite, consumo, disponível e bloqueio |
| `GET /limites/uso/historico/` | conta autenticada | histórico paginado da própria conta |
| `GET /limites/planos/` | conta autenticada | catálogo ativo por conta |
| `PATCH /limites/instituicoes/{id}/plano/` | mantenedor Vitis Souls | troca auditada de plano |

Exemplo de `GET /limites/uso/`:

```json
{
  "ciclo": "2026-08",
  "limite_percentual": "171.0000",
  "consumido_percentual": "12.3456",
  "disponivel_percentual": "158.6544",
  "bloqueado": false
}
```

### Competência mensal

O plano é cobrado por conta/mês, então o percentual é contado dentro de uma
**competência** (`ciclo`, no formato `YYYY-MM`, mês-calendário em UTC). O
consumo de um mês não é somado ao do mês seguinte: na virada, `consumido_percentual`
volta a zero e a conta destrava sozinha.

Cada `ConsumoIA` grava a competência no momento do débito e nunca a recalcula —
o registro continua *append-only* e auditável, e mudar a regra de janela no
futuro não reescreve retroativamente o que já foi cobrado. `GET
/limites/uso/historico/` expõe `ciclo` em cada item. A regra vive em
`backend/limites/ciclo.py`.

O PATCH do plano recebe `{ "plano": "PRISMA_PRO", "motivo": "upgrade" }`.
Motivo vazio retorna `400`. Usuário acadêmico retorna `403`, instituição
inexistente retorna `404` e a instituição mantenedora retorna `400`.

## Tutor

| Método e rota | Permissão | Resultado |
|---|---|---|
| `GET/POST /memoria/conversas/` | aluno | lista ou cria conversa própria |
| `GET /memoria/conversas/{id}/` | dono da conversa | mensagens próprias |
| `POST /memoria/conversas/{id}/mensagens/` | dono da conversa | grava pergunta e resposta |
| `GET/PATCH /memoria/tutor/configuracao/` | aluno | preferências do tutor |

`POST` de mensagem recebe `{ "conteudo": "..." }`. Se não houver percentual
disponível, a resposta é `422` com código `limite_uso_excedido`; nenhuma
mensagem de tutor é gravada sem uma chamada de IA concluída.

## Materiais e simulados

| Método e rota | Permissão | Resultado |
|---|---|---|
| `GET /conteudo/materiais/` | usuário autenticado | materiais oficiais do tenant e próprios rascunhos |
| `POST /conteudo/materiais/gerar/` | aluno/professor | gera rascunho e debita percentual |
| `GET /conteudo/simulados/` | aluno | próprios simulados |
| `POST /conteudo/simulados/gerar/` | aluno | cria simulado e questões |
| `GET /conteudo/simulados/{id}/` | aluno dono | questões sem gabarito durante a prova |
| `POST /conteudo/simulados/{id}/questoes/{questao_id}/responder/` | aluno dono | registra alternativa |
| `POST /conteudo/simulados/{id}/finalizar/` | aluno dono | calcula resultado e revela correção |

Geração sem limite retorna `422`. Rascunho de outro aluno e simulado de outro
usuário retornam `404`, evitando confirmação de existência entre tenants.

### Origem das questões do simulado

As questões vêm **exclusivamente** da resposta do modelo, num contrato de saída
estruturada (`{"questoes": [{"enunciado", "alternativas", "gabarito"}]}`,
declarado no próprio prompt). Se o provedor não honrar o contrato — JSON
inválido, quantidade diferente da pedida, alternativa vazia, gabarito fora de
`A–D` — **nenhum simulado é criado** e a rota responde `503` com código
`simulado_indisponivel`. Falha do provedor responde `503` com `erro_provedor`.

O percentual já debitado permanece registrado nesses casos: a chamada
aconteceu e custou. Fabricar questão para "aproveitar" o débito é exatamente o
que produzia simulado com gabarito fixo. A correção comentada por questão ainda
não é persistida — `correcao_comentada` hoje só chega ao prompt.

## Dashboard e agenda

| Método e rota | Permissão | Resultado |
|---|---|---|
| `GET /aluno/dashboard/` | aluno | métricas, cota, progresso e itens recentes |
| `GET/POST /aluno/agenda/` | aluno | lista ou cria item próprio |
| `PATCH /aluno/agenda/{id}/` | aluno dono | altera/conclui item próprio |

Filtros `de` e `ate` da agenda usam ISO-8601. Data inválida retorna `400`.

## Uma chamada de IA por conta de cada vez

Toda rota que aciona o gateway (tutor, geração de material, geração de
simulado) responde `409` com código `chamada_em_andamento` se a conta já tiver
uma chamada em curso. É o teto que mantém o estouro do plano limitado a uma
única chamada: o portão de limite lê o consumido, e chamadas simultâneas ainda
não debitaram. Chamada pendente mais velha que a janela de abandono é tratada
como órfã, para que um processo morto no meio não trave a conta.

Falha do provedor responde `503` (`erro_provedor`) nas três rotas.

## Contabilidade técnica

O contrato de produto é percentual. O gateway pode conservar unidades brutas
retornadas pelo fornecedor apenas como telemetria técnica server-side; elas não
são saldo, preço, permissão ou parâmetro que o frontend possa controlar. O
registro comercial é `ConsumoIA.percentual`, com fornecedor, modelo, tarefa,
custo bruto técnico e referência idempotente à chamada.

**Estado final:** CONTRATO VIGENTE localmente; integração de tela e chamada de
provedor real permanecem pendências explícitas. Identidade: **Code Review**.
