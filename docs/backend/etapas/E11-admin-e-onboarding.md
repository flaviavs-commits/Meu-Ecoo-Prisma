# E11 - Admin e onboarding da escola

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
> **Depende de:** E04 · **Destrava:** -
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Dar a equipe interna uma forma real de colocar uma escola nova para funcionar:
criar a instituicao, o diretor, o pool de creditos inicial - e permitir que o
diretor toque a operacao dali em diante.

Nao ha autocadastro. Este e o **unico** caminho de entrada de um cliente.

## 2. Pre-requisitos

- E04 `CONCLUIDA` (permissoes + mixin destrutivo + auditoria)
- E05 recomendada (para ja alocar credito inicial). Sem ela, entregue o resto e
  registre a pendencia.

## 3. Escopo

**Entra:** Django Admin configurado e utilizavel, fluxo de criacao de
instituicao + diretor, convite de professor, remocao de usuario (destrutiva),
protecao do admin.

**Nao entra:** painel administrativo proprio - decisao explicita de deixar para
depois.

## 4. Decisao travada: Django Admin nesta fase

O Django Admin foi considerado "feio e confuso", e a intencao declarada e ter um
painel proprio no futuro, inspirado num painel interno que a empresa ja opera
(ver [`../FERRAMENTAS-E-ECOSSISTEMA.md`](../FERRAMENTAS-E-ECOSSISTEMA.md)).

Ainda assim, o Admin fica **nesta fase**, porque ja vem pronto, cobre o caso de
uso interno e nao gasta o tempo que a fundacao precisa. O painel proprio e etapa
futura, com escopo proprio.

O que **deve** ser feito: deixar o Admin utilizavel de verdade - `list_display`,
busca, filtro, campos agrupados. Um Admin cru, com 40 campos em ordem aleatoria,
e o que gera a fama de confuso.

O que **nao** deve: gastar tempo customizando visual do Admin. Se o visual
importa, a resposta e o painel proprio, nao maquiar o Admin.

## 5. Como fazer

### 5.1 Fluxo de onboarding

Criar escola na mao, tela por tela, e onde se erra: cria a instituicao, esquece
o diretor, esquece o credito, e o cliente entra num sistema pela metade.

Entregue como **um comando de management**, transacional:

```bash
railway run python manage.py criar_instituicao \
    --nome "Colegio Exemplo" \
    --documento "00.000.000/0001-00" \
    --diretor-email "diretor@exemplo.edu.br" \
    --diretor-nome "Nome do Diretor" \
    --creditos-iniciais 100000
```

O comando cria a instituicao, o usuario diretor e o lancamento inicial de
credito **numa transacao**. Ou tudo existe, ou nada existe.

Isso segue a preferencia do padrao de qualidade por automacao reutilizavel em
vez de edicao manual: o comando vira patrimonio, o clique nao.

O diretor **nao** recebe senha definida por ninguem - recebe um fluxo de
definicao de senha (E03). Senha inicial enviada por e-mail ou dita por telefone
e pratica ruim que sobrevive por anos.

### 5.2 Django Admin utilizavel

Um `admin.py` por app, registrando so o que a equipe interna precisa operar.

| Model | O que expor |
|-------|-------------|
| `Instituicao` | nome, documento, ativa, saldo, contagem de usuarios |
| `Usuario` | nome, e-mail, perfil, instituicao, ativo, consentimento pendente |
| `Lancamento` | **somente leitura** - e append-only |
| `RegistroDeAuditoria` | **somente leitura** |
| `ChamadaIA` | somente leitura, para investigar consumo |

Cuidados:

- `Lancamento` e `RegistroDeAuditoria` com `has_change_permission = False` e
  `has_delete_permission = False`. Admin que edita ledger destroi a contabilidade.
- Filtro por instituicao em tudo.
- **Nunca** exibir hash de senha, token ou conteudo de conversa de aluno.
- `raw_id_fields` em FK de tabela grande - senao o Admin tenta carregar 5 mil
  alunos num `<select>`.

### 5.3 Convite de professor

O padrao correto ja existe na tela do diretor (`mockup/diretor.html`): convite
por e-mail, com estado "convite pendente".

- diretor convida por e-mail;
- o convidado define a propria senha;
- convite expira;
- **nunca** convite por link publico que qualquer um usa - isso e o modelo antigo
  e foi removido do produto.

Se ainda nao houver envio de e-mail configurado, entregue o fluxo com o envio
atras de um adaptador e registre a pendencia. Nao invente credencial de SMTP.

### 5.4 Remocao de usuario - acao destrutiva

E uma das tres acoes destrutivas. Usa o mixin de E04.

- e **desativacao**, nao exclusao - notas, faltas e historico continuam
  existindo;
- exige confirmacao e motivo;
- grava auditoria;
- usuario desativado nao autentica (E03 ja garante).

Excluir de verdade e assunto de LGPD (direito de eliminacao) e envolve
anonimizacao - **nao** e esta acao. Ver
[contrato de LGPD](../contratos/LGPD-E-DADOS-SENSIVEIS.md), item 6.

### 5.5 Proteger o admin

O Admin da acesso a dado de milhares de menores. Ele e o alvo mais valioso do
sistema.

- URL do admin **nao** e `/admin/` - use um caminho proprio por variavel de
  ambiente;
- so `is_staff` da equipe interna entra. Diretor de escola **nao** e staff;
- rate limit no login do admin;
- `SECURE_SSL_REDIRECT`, cookie seguro e sessao curta em producao;
- considere 2FA e registre a recomendacao - decisao humana.

### 5.6 TDD - ordem sugerida

1. Comando cria instituicao + diretor + credito inicial numa transacao.
2. Comando com dado invalido nao cria **nada** (transacao desfeita).
3. Comando e idempotente ou falha claro ao repetir documento ja existente.
4. Diretor criado nao tem senha utilizavel ate definir a propria.
5. Diretor **nao** e `is_staff` e nao acessa o admin.
6. `Lancamento` nao pode ser editado nem apagado pelo admin.
7. Remocao de usuario sem confirmacao -> 400.
8. Remocao desativa e preserva o historico.
9. Usuario desativado nao autentica.
10. Convite de professor cria estado pendente e nao cria usuario ativo.

## 6. Contrato de saida

- comando `criar_instituicao` transacional e testado
- Django Admin utilizavel, com ledger e auditoria em somente leitura
- convite de professor por e-mail, com estado pendente
- remocao de usuario como desativacao auditada
- admin em caminho proprio, restrito a equipe interna

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Escola criada pela metade | Comando transacional |
| Admin editando ledger | Somente leitura, testado |
| Diretor com acesso ao admin | `is_staff` so para equipe interna. Teste 5. |
| Admin em URL previsivel | Caminho por variavel de ambiente |
| Senha inicial trafegando | Fluxo de definicao pelo proprio usuario |
| Sem provedor de e-mail | Adaptador + pendencia registrada |
| 2FA | Recomendacao registrada, decisao humana |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

_(vazio - primeira entrada e sua)_

## 9. Criterio de pronto

- [ ] Os 10 testes do item 5.6 passam - saida real no diario
- [ ] Comando rodado de verdade contra o banco - saida colada no diario
- [ ] Rollback verificado com dado invalido
- [ ] Ledger e auditoria em somente leitura no admin - testado clicando
- [ ] Admin fora de `/admin/`, restrito a equipe interna
- [ ] Nenhum dado sensivel exposto em listagem do admin
- [ ] Pendencia de e-mail e recomendacao de 2FA registradas
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] `README.md` da raiz documenta como criar uma escola nova
- [ ] Commit feito, so com arquivos desta etapa
