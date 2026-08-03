# Contrato: convencoes de API

> Regra unica de como a API do Prisma responde. Definida uma vez, respeitada por
> todas as etapas. Mudar isto e mudanca quebradora - exige decisao explicita e
> registro no [`IA.md`](../../../IA.md).

## 1. Prefixo e versao

Toda rota vive sob `/api/v1/`.

A versao existe porque o consumidor e uma SPA que sera publicada separadamente
do backend: as duas nem sempre sobem juntas. `v1` so muda para `v2` em quebra de
contrato real.

## 2. Nomes

- Caminho de recurso: **plural, kebab-case** - `/api/v1/turmas/`, `/api/v1/creditos/lancamentos/`
- Campo de JSON: **snake_case** - `data_nascimento`, `instituicao_id`
- Nunca misture `camelCase` e `snake_case` na mesma resposta. O frontend adapta.

Vocabulario de dominio (aluno, professor, diretor, turma, credito...) segue o
[glossario](GLOSSARIO.md). Nome de campo em portugues, igual ao dominio.

## 3. Resposta de sucesso

Use o formato nativo do DRF, **sem envelope**. Um recurso e um objeto JSON; uma
lista e uma lista paginada.

```json
GET /api/v1/turmas/12/
{
  "id": 12,
  "nome": "3o ano B",
  "instituicao_id": 3,
  "criado_em": "2026-08-01T14:20:00Z"
}
```

Envelope (`{"data": ..., "error": null}`) foi descartado: o DRF ja distingue
sucesso de erro pelo status HTTP, e o envelope so adiciona ruido em toda
resposta.

## 4. Paginacao

Toda listagem e paginada, **inclusive as que hoje parecem pequenas**. Uma turma
com 40 alunos vira uma instituicao com 5 mil.

```json
{
  "count": 137,
  "next": "https://.../api/v1/alunos/?page=3",
  "previous": "https://.../api/v1/alunos/?page=1",
  "results": [ ... ]
}
```

Padrao: `PageNumberPagination`, 25 por pagina, maximo 100 via `?page_size=`.

## 5. Erro

Formato unico, para o frontend nunca precisar adivinhar:

```json
{
  "erro": {
    "codigo": "saldo_insuficiente",
    "mensagem": "A turma nao tem creditos suficientes para esta acao.",
    "detalhes": { "saldo_atual": 0 }
  }
}
```

| Campo | Papel |
|-------|-------|
| `codigo` | `snake_case` estavel, para o frontend decidir comportamento. Nunca traduza. |
| `mensagem` | Texto em portugues, seguro para mostrar ao usuario final |
| `detalhes` | Opcional. Contexto estruturado. Nunca contem dado de outra instituicao. |

Erro de validacao de campo mantem o mapa do DRF dentro de `detalhes`:

```json
{
  "erro": {
    "codigo": "validacao",
    "mensagem": "Alguns campos estao invalidos.",
    "detalhes": { "email": ["Informe um e-mail valido."] }
  }
}
```

Isso e implementado como um **exception handler unico** do DRF, na E01. Nenhuma
view formata erro na mao.

## 6. Status HTTP

| Status | Quando |
|--------|--------|
| 200 | Sucesso com corpo |
| 201 | Recurso criado |
| 204 | Sucesso sem corpo (remocao) |
| 400 | Entrada invalida |
| 401 | Sem autenticacao ou token expirado |
| 403 | Autenticado, mas sem permissao - **inclui tentar acessar outra instituicao** |
| 404 | Recurso nao existe |
| 409 | Conflito de estado (ex.: confirmar prova ja oficial) |
| 422 | Regra de negocio recusou uma entrada valida (ex.: saldo insuficiente) |
| 429 | Rate limit |
| 500 | Falha interna - **nunca** com stack trace no corpo |

**Regra importante de seguranca:** acessar recurso de outra instituicao responde
`404`, nao `403`. Responder 403 confirmaria que aquele id existe - e vazamento
de informacao entre clientes. Ver [E02](../etapas/E02-nucleo-de-dados-e-multitenancy.md).

## 7. Datas, horas e numeros

- Data e hora: **ISO 8601 em UTC**, com `Z`. O fuso e problema de apresentacao.
- Data pura (nascimento, dia de aula): `YYYY-MM-DD`.
- Dinheiro e credito: **nunca** `float`. `Decimal` no Python, string ou inteiro
  na API. Ver [E05](../etapas/E05-creditos-ledger.md).

## 8. Autenticacao

`Authorization: Bearer <access_token>`. Detalhe do fluxo em
[E03](../etapas/E03-autenticacao-jwt.md).

Toda rota e autenticada por padrao (`DEFAULT_PERMISSION_CLASSES` =
`IsAuthenticated`). Rota publica e excecao explicita e justificada - hoje so o
health check.

## 9. Acao destrutiva

As tres acoes destrutivas listadas na [visao geral](../VISAO-GERAL.md) usam
`POST` numa sub-rota de acao, nao `DELETE` direto:

```
POST /api/v1/alunos/42/remover/
{ "confirmacao": true, "motivo": "transferencia de escola" }
```

O padrao completo (o que exigir, como validar) e definido em
[E04](../etapas/E04-autorizacao-e-perfis.md) e reusado sem variacao.

## 10. Checklist ao criar um endpoint

- [ ] Esta sob `/api/v1/` e o nome segue o glossario
- [ ] Listagem e paginada
- [ ] Entrada validada por serializer, nao na view
- [ ] Filtra por instituicao do usuario logado
- [ ] Permissao checada **por objeto**, nao so por rota
- [ ] Erro sai no formato do item 5, pelo handler unico
- [ ] Responde 404 (nao 403) para recurso de outra instituicao
- [ ] Tem teste do caminho feliz e do caminho negado
