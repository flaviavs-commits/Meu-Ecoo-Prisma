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
  "limite_percentual": "171.0000",
  "consumido_percentual": "12.3456",
  "disponivel_percentual": "158.6544",
  "bloqueado": false
}
```

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

## Dashboard e agenda

| Método e rota | Permissão | Resultado |
|---|---|---|
| `GET /aluno/dashboard/` | aluno | métricas, cota, progresso e itens recentes |
| `GET/POST /aluno/agenda/` | aluno | lista ou cria item próprio |
| `PATCH /aluno/agenda/{id}/` | aluno dono | altera/conclui item próprio |

Filtros `de` e `ate` da agenda usam ISO-8601. Data inválida retorna `400`.

## Contabilidade técnica

O contrato de produto é percentual. O gateway pode conservar unidades brutas
retornadas pelo fornecedor apenas como telemetria técnica server-side; elas não
são saldo, preço, permissão ou parâmetro que o frontend possa controlar. O
registro comercial é `ConsumoIA.percentual`, com fornecedor, modelo, tarefa,
custo bruto técnico e referência idempotente à chamada.

**Estado final:** CONTRATO VIGENTE localmente; integração de tela e chamada de
provedor real permanecem pendências explícitas. Identidade: **Code Review**.
