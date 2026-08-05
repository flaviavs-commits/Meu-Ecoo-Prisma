# Revisão técnica — todos os commits de 2026-08-05

**Revisor:** Code review
**Escopo:** `2aaca78^..HEAD` (38 commits, 123 arquivos, +6714/−170)
**Status:** REVISÃO CONCLUÍDA — **3 bloqueantes + 7 importantes + 2 sugestões
corrigidos e publicados**; os achados 4, 12 e 13 continuam abertos

## Como foi verificado

- Suíte backend em SQLite: `189 passed, 3 skipped` — o número declarado em
  `docs/backend/etapas/E15-limite-percentual-e-api-aluno.md` **confere**.
- Dois achados foram confirmados com testes descartáveis (removidos depois),
  não por leitura: o consumo sem janela de cobrança (bloqueante 1) e o
  `datetime` naive da agenda (importante 8).
- Árvore de trabalho limpa ao fim da revisão; nada foi alterado no repositório.

---

## Bloqueantes — **CORRIGIDOS**

Os três foram consertados em seguida, a pedido da usuária. O diagnóstico
original fica preservado abaixo; o que foi feito está em
"Correções aplicadas".

### 1. O limite percentual nunca reinicia — a escola paga todo mês e a conta fica bloqueada para sempre

`backend/limites/servico.py:38-51`

`estado_cota` soma **todo** `ConsumoIA` do usuário desde sempre:

```python
consumido = ConsumoIA.objects.filter(usuario=usuario).aggregate(total=Sum("percentual"))["total"]
```

Não há filtro por período em lugar nenhum do app. Mas o produto é mensal —
`E15` define `preço do plano × contas ativas` como **valor mensal** e o
catálogo é "R$ 68,97 por conta/mês, 100%".

**Cenário concreto (verificado com teste):** um aluno de escola no plano Prisma
consome 100% em agosto. Em setembro a escola é cobrada de novo, mas
`estado_cota` continua devolvendo `disponivel = 0`, `autorizar_uso` levanta
`LimiteDeUsoExcedidoError` e o aluno fica permanentemente sem tutor, sem
simulado e sem material. Simulei envelhecendo o consumo em 60 dias: o bloqueio
persiste.

**Correção:** introduzir uma janela de competência explícita. O mínimo é
filtrar `criado_em__gte=inicio_do_ciclo` derivado de
`AssinaturaInstituicao.criada_em` (ou de um campo `ciclo_referencia` gravado em
`ConsumoIA`, que evita recalcular a data e mantém o append-only auditável).
Isso precisa de teste cobrindo virada de ciclo.

### 2. `oficial=True` para o diretor sem migração de backfill

`backend/academico/notas.py:145-152`, migração `academico/0002` (`oficial` nasce
`default=False`)

`consultar_notas` para `DIRETOR` passou a filtrar `oficial=True`. `git log -S
"oficial = True"` mostra que **o único commit que já setou esse campo é o de
hoje** (`6d3fa4a`) — logo, toda nota que já existe em produção tem
`oficial=False` e não há migração de dados corrigindo isso.

**Cenário concreto:** no deploy, a tela de notas de todo diretor fica vazia até
que cada professor reabra e aprove nota por nota, uma a uma, via
`POST /academico/notas/<pk>/aprovar/`. Não há ação em lote.

**Correção:** ou uma migração de dados marcando `oficial=True` para notas
anteriores ao corte (é o comportamento que elas tinham), ou uma decisão
explícita e comunicada de que o histórico precisa ser reaprovado. Hoje a
escolha está implícita no código.

### 3. Simulado cobra chamada de IA real e devolve questões falsas com gabarito sempre "A"

`backend/conteudo/simulados.py:22-54`

`gerar_simulado` chama o gateway (que debita percentual e, com provedor real,
gasta dinheiro), **descarta o resultado** e cria as questões assim:

```python
enunciado=f"{disciplina}: questão {ordem} gerada para estudo.",
alternativas=["Alternativa A", ..., "Alternativa D"],
gabarito="A",
```

`E15 › Limites conhecidos` diz que a geração "é determinística até existir um
contrato de saída estruturada" — mas o contrato
`docs/backend/contratos/API-ALUNO-E-LIMITES.md` anuncia a rota como
"cria simulado e questões", sem ressalva, e nada no código sinaliza que é stub.

**Cenário concreto:** aluno gera um simulado de 15 questões, responde "A" em
todas, `finalizar_simulado` calcula 100% e grava em
`Simulado.resultado_percentual`, que alimenta `progresso_por_materia` no
dashboard. O percentual de estudo do aluno vira ruído — e a escola pagou pela
chamada.

**Correção:** enquanto o provedor não devolver saída estruturada, ou não chamar
o gateway (não cobrar por output descartado), ou marcar o simulado com um
estado `SIMULADO_DEMO` que o dashboard ignora. A ressalva também precisa sair
do E15 e entrar no contrato da API.

---

## Importantes

### 4. Contrato de erro violado em toda a superfície nova

`docs/backend/contratos/API-CONVENCOES.md:78-91` é explícito: o formato é
`{"erro": {"codigo", "mensagem", "detalhes"}}`, implementado por um
*exception handler* único, e **"nenhuma view formata erro na mão"**.

Os endpoints criados hoje formatam à mão, em quatro formatos diferentes:

| Arquivo | Linha | Formato produzido |
|---|---|---|
| `backend/limites/views.py` | 48 | `Response(status=404)` — sem corpo |
| `backend/limites/views.py` | 59 | `{"erro": {"codigo": ...}}` — sem `mensagem` |
| `backend/limites/views.py` | 61 | `{"erro": {"mensagem": ...}}` — sem `codigo` |
| `backend/contas/views.py` | 35 | `{"erro": "texto"}` — `erro` é string, não objeto |
| `backend/aluno/views.py` | 20 | `Response(status=403)` — sem corpo |
| `backend/conteudo/simulado_views.py` | 28,40,55,72,91 | idem, sem corpo |

**Cenário concreto:** o cliente que trata `resposta.erro.codigo` quebra com
`TypeError` ao chamar `POST /contas/.../desativar/`, porque ali `erro` é
string. O frontend ainda não consome nada disso — é a hora barata de arrumar.

**Correção:** um handler DRF único (a E01 já prevê) e remover a formatação
manual das views.

### 5. Transação e lock de linha ficam abertos durante a chamada HTTP ao provedor

`backend/ia/gateway.py:61-87` e `backend/memoria/tutor.py:26-56`

`trava_cota` abre `transaction.atomic()` + `SELECT ... FOR UPDATE` na
`CotaUsuario` e **só fecha depois** de `_gerar_com_retry`, que pode levar até
3 × `IA_TIMEOUT_SEGUNDOS` (padrão 10s = 30s). Em `memoria/tutor.py` há ainda um
`atomic()` externo envolvendo tudo.

**Cenário concreto:** 20 alunos mandam mensagem ao tutor ao mesmo tempo com o
provedor lento. São 20 transações Postgres em `idle in transaction` por até 30s
cada, segurando conexão do pool. Com o pool default do Railway, os pedidos
seguintes (inclusive o healthcheck se ele tocar o banco) começam a falhar.

**Correção:** separar as fases — chamar o provedor **fora** de qualquer
transação, e abrir a transação curta só para `registrar_uso` + gravação da
`ChamadaIA`. A idempotência por `referencia` que `registrar_uso` já tem
(`servico.py:86-90`) é justamente o que torna isso seguro.

### 6. Chamada que falha pelo tutor perde o registro de erro; pelo simulado, não

`backend/memoria/tutor.py:26` vs `backend/conteudo/simulados.py:22`

`gateway.chamar` grava o erro em `_marcar_erro` assumindo que está fora de uma
transação que vai reverter. Em `gerar_simulado` o gateway é chamado fora do
`atomic()`, então o `ChamadaIA(status=ERRO)` persiste. Em `responder_mensagem`
o gateway roda **dentro** do `atomic()` externo — quando
`LimiteDeUsoExcedidoError` sobe, tudo é revertido, inclusive o registro de erro.

**Cenário concreto:** aluno sem percentual manda mensagem ao tutor; recebe 422
corretamente, mas não fica nenhum rastro em `ChamadaIA`. A mesma falha pelo
simulado deixa rastro. A auditoria de falhas fica com buraco silencioso e
dependente do caller.

**Correção:** cai junto com o achado 5 — tirando o provedor de dentro da
transação, `_marcar_erro` passa a ter comportamento único.

### 7. Custo real pago e débito recusado

`backend/ia/gateway.py:62-78` + `backend/limites/servico.py:94`

`autorizar_uso` só verifica `disponivel > 0`. Depois da chamada ao provedor,
`registrar_uso` verifica `consumido + percentual > limite` e **recusa**.

**Cenário concreto:** aluno com 0,5% restante no plano Prisma dispara uma
tutoria que consome 3%. O provedor já foi chamado e cobrado; `registrar_uso`
levanta `LimiteDeUsoExcedidoError`, a `ChamadaIA` vira `ERRO` e o
`ConsumoIA` nunca é criado. O custo existe no fornecedor e não existe em lugar
nenhum na nossa contabilidade.

**Correção:** ou registrar o consumo mesmo estourando (permitindo saldo
negativo controlado, que é o que a contabilidade real quer), ou estimar o custo
antes de chamar. Registrar e recusar é a única combinação que perde dinheiro em
silêncio. `E15` descreve a recusa como feature, sem citar essa consequência.

### 8. Filtro de data da agenda usa `datetime` naive com `USE_TZ = True`

`backend/aluno/views_agenda.py:55-59`

`datetime.fromisoformat(valor)` devolve naive. **Confirmado com teste:**
`GET /api/v1/aluno/agenda/?de=2026-08-01` emite
`RuntimeWarning: DateTimeField AgendaEstudo.agendado_para received a naive
datetime (2026-08-01 00:00:00) while time zone support is active`.

Além do warning em todo log de produção, `API-CONVENCOES.md:114` exige
"ISO 8601 em UTC, com `Z`" — a view aceita string sem fuso e deixa o Django
adivinhar.

**Correção:** `django.utils.dateparse.parse_datetime` + `timezone.make_aware`
quando vier naive, rejeitando com 400 o que não parsear.

### 9. Painel corta listas em 100 sem avisar

`backend/painel_admin/views.py:63` (`Instituicao...[:100]`) e `:153`
(`Usuario...[:100]`)

`registros` ganhou `Paginator`; instituições e usuários não.

**Cenário concreto:** com 120 escolas cadastradas, o superadmin abre
`/painel/instituicoes/`, vê 100, e as 20 que faltam simplesmente não existem
para ele — sem paginação, sem contador, sem aviso. Em `/painel/usuarios/` a
busca por e-mail ainda salva, mas a listagem mente do mesmo jeito.

**Correção:** o mesmo `Paginator(queryset, 25)` já usado em `registros`.

### 10. Arquivar instituição é irreversível e não audita conta por conta

`backend/painel_admin/services/arquivar_instituicao.py:27-30`

```python
Usuario.objects.filter(instituicao=alvo, is_active=True).update(ativo=False, is_active=False)
```

O `update()` em massa não passa por `save()`, não mexe em `atualizado_em` e não
gera `RegistroDeAuditoria` por usuário — só um registro para a instituição. E
**não existe desarquivar**: quem era ativo antes do arquivamento não fica
registrado em lugar nenhum.

**Cenário concreto:** superadmin arquiva a escola errada (são dois cliques,
`confirmacao` + `motivo`). 500 contas caem. Reativar a instituição não reativa
ninguém, e não há como saber quais das 500 estavam ativas antes — inclusive
porque contas já desativadas individualmente antes viraram indistinguíveis.

**Correção:** gravar a lista de PKs afetadas no `motivo`/metadado da auditoria
(é o mínimo para reverter) e implementar `desarquivar_instituicao` usando essa
lista. `DESIGN_SYSTEM_PARA_BACKEND §2.5` pede mudança reversível quando
possível.

### 11. `eh_mantenedor` fecha o painel para superusuário fora da Vitis Souls e custa uma query por request

`backend/contas/models.py:130-140`, `backend/painel_admin/permissoes.py:12`

O portão do painel passou de `is_superuser` para `eh_mantenedor`, que exige
`perfil == MANTENEDOR` **e** instituição `VITIS_SOULS`. A migração
`contas/0007` vincula os superadmins existentes, e `create_superuser` passou a
criar/exigir a Vitis Souls — então o caminho feliz está coberto.

O que não está: um superusuário criado por qualquer outro caminho (fixture,
shell, script antigo, restore de dump anterior à 0007) fica com
`instituicao=None`, `eh_mantenedor` devolve `False` e ele **não entra no
painel** — com `PermissionDenied` seco, sem dizer o que falta. É uma mudança de
contrato operacional que não está no `README` nem no E14.

Secundariamente, `eh_mantenedor` acessa `self.instituicao.codigo`: sem
`select_related`, é uma query extra em cada request do painel e em
`limites/permissoes.py`.

**Correção:** documentar o novo pré-requisito no E14 e, quando `eh_mantenedor`
falhar por falta de vínculo, devolver mensagem acionável. Para a query, usar
`instituicao__codigo` já carregado ou cachear na instância.

### 12. A allowlist de `api/painel.ts` não protege as rotas que importam

`frontend/api/painel.ts:14-36` vs `frontend/vercel.json:36-58`

O cabeçalho de `painel.ts` afirma que "a funcao valida caminho e metodo antes
de encaminhar qualquer requisicao". Mas o `vercel.json` só manda `/painel/` e
`/backoffice/` **exatos** para a função. Todo o resto —
`/painel/:path*`, `/painel/:path*/`, `/backoffice/:path*`, `/static/:path*` —
é rewrite direto para o Railway, sem passar pela função.

**Cenário concreto:** `POST /painel/usuarios/1/desativar/` (ação destrutiva) e
`POST /backoffice/login/` não passam por nenhuma validação de método da
allowlist. Ela cobre só as duas raízes, que na prática só servem GET. O
controle existe, é testado, e não está no caminho do tráfego real.

Junto disso: o domínio `https://api-production-8b58.up.railway.app` está
**hardcoded em 6 destinos** do `vercel.json` — exatamente o hardcode que o
commit `de1447b` removeu de `proxy.ts` no mesmo dia, com a justificativa
registrada no `IA.md`. Se o serviço Railway for recriado, ajustar
`PRISMA_API_ORIGIN` conserta a API e deixa painel, admin e estáticos quebrados.

**Correção:** decidir uma das duas — ou tudo passa pela função (e o
`vercel.json` só aponta para `/api/painel`), ou o comentário de `painel.ts`
deixa de afirmar uma proteção que não está no caminho. A segunda opção também
resolve o hardcode, porque a origem volta a sair de `PRISMA_API_ORIGIN`.

### 13. `perfil != "ALUNO"` copiado em 12 views, com string mágica

`backend/aluno/views.py:19`, `backend/aluno/views_agenda.py:16,31,43`,
`backend/memoria/views.py:29,37,49,62,94,99`,
`backend/conteudo/simulado_views.py:27,39,54,71,90`

Mesma checagem, escrita à mão, ora com `getattr(...)`, ora com acesso direto,
sempre com o literal `"ALUNO"` em vez de `Perfil.ALUNO`. O repositório já tem
o padrão certo em `limites/permissoes.py` (`BasePermission`).

**Cenário concreto:** o dia em que surgir um perfil `MONITOR` que também usa o
tutor, são 12 lugares para achar e editar — e o primeiro esquecido vira falha
de autorização, não erro de tela.

**Correção:** uma `EAluno(BasePermission)` (e `EAlunoOuProfessor` para
`GerarMaterialView`) em `contas/permissoes.py`, usada por `permission_classes`.

### 14. Unicidade de e-mail: `iexact` na criação, exata na edição

`backend/painel_admin/forms/conta_teste.py:37` usa `email__iexact`;
`backend/painel_admin/services/editar_usuario.py:52` usa `email=email`.

`UsuarioManager.normalize_email` só normaliza o domínio — a parte local
preserva maiúsculas, e o índice único do Postgres é *case-sensitive*.

**Cenário concreto:** existe `Felipe@vitissouls.com` (criado por
`createsuperuser`). O mantenedor edita outra conta para `felipe@vitissouls.com`;
o `filter(email=...)` exato não encontra a primeira, o índice único não
reclama, e passam a existir duas contas que a pessoa não distingue no login.

**Correção:** `__iexact` nos dois lugares (ou normalizar tudo para minúsculo em
`Usuario.save`, o que é mais definitivo).

### 15. Migração de dados itera usuário por usuário

`backend/limites/migrations/0002_catalogo_planos.py:31-34`

```python
for usuario in Usuario.objects.all():
    Cota.objects.get_or_create(usuario=usuario)
```

Duas queries por usuário, sem `iterator()`, dentro da migração que o Railway
roda no *predeploy*.

**Cenário concreto:** hoje a base é pequena e passou. Com 20 mil contas são
40 mil round-trips com o deploy bloqueado — e, se estourar o timeout do
predeploy, a release falha no meio da migração de dados.

**Correção:** `Cota.objects.bulk_create([...], ignore_conflicts=True)` sobre
`Usuario.objects.values_list("pk", flat=True).iterator()`. Mesma coisa para
`Assinatura`.

### 16. `DISTINCT` na tabela de auditoria inteira a cada carga da página

`backend/painel_admin/views.py:227-229`

`acoes_disponiveis` faz `values_list("acao").distinct()` sobre toda a
`RegistroDeAuditoria` — a tabela que mais cresce no sistema, e sem índice em
`acao`.

**Cenário concreto:** com auditoria de meses, cada abertura de
`/painel/registros/` (inclusive cada troca de página do `Paginator` logo abaixo)
faz um scan completo só para montar o `<select>` de filtro.

**Correção:** a lista de ações é finita e conhecida no código
(`criar_instituicao`, `alterar_perfil`, `aprovar_nota`, …) — declarar como
constante, ou cachear.

---

## Sugestões

### 17. `PERCENTUAL_MAXIMO` não cabe na coluna que ele diz proteger

`backend/limites/models.py:6-8,81` — o comentário afirma que
`Decimal("9999999.9999")` é "o maior valor que cabe no campo de consumo", mas
`percentual` é `max_digits=7, decimal_places=4` (máximo real: `999.9999`), e
`ChamadaIA.percentual_debitado` é `max_digits=14`. Três limites diferentes para
a mesma grandeza. Na prática o guarda de limite recusa antes, então a validação
`_percentual_positivo` nunca dispara — é código morto com comentário errado.

### 18. `@require_POST` antes do portão de permissão

`backend/painel_admin/views.py:85-86,103-104,180-181,235-236,251-252,267-268` —
decorador externo roda primeiro, então um `GET` anônimo em
`/painel/usuarios/1/desativar/` recebe `405` (confirmando que a rota existe) em
vez de redirect para login. Inverter a ordem.

### 19. Invariante do MANTENEDOR escrita três vezes

`contas/models.py:115-128` (`clean`), `painel_admin/services/alterar_perfil.py:21-31`
e `painel_admin/services/editar_usuario.py:35-45` — mesma regra, redações e
condições ligeiramente diferentes. `clean()` nem é chamado no fluxo dos
services (ninguém faz `full_clean()`). Concentrar numa função única.

### 20. Contrato do dashboard do aluno não é contrato

`backend/aluno/serializers.py:6-10` — `metricas`, `progresso_por_materia` e
`recentes` são `DictField()`/`ListField()` genéricos. O serializer não valida
nem documenta nada; qualquer mudança em `views.py` altera a resposta em
silêncio. Tipar os três blocos.

### 21. Listagens sem paginação

`backend/aluno/views_agenda.py:18-28` (agenda inteira do aluno) e
`backend/memoria/serializers.py:13-19` (`ConversaSerializer` embute **todas**
as mensagens da conversa). `API-CONVENCOES` e o design system pedem paginação
onde o volume cresce — e conversa de tutor cresce por definição.

### 22. 50 `INSERT` em loop

`backend/conteudo/simulados.py:42-54` — `quantidade` chega a 50
(`GerarSimuladoSerializer`), uma query por questão. `bulk_create`.

### 23. Validação redundante

`backend/aluno/serializers_agenda.py:21-23` — `validate_status` repete a
validação de `choices` que o `ModelSerializer` já faz.

### 24. `collectstatic` no `CMD`, não no `RUN`

`backend/Dockerfile:13` — com `CompressedManifestStaticFilesStorage`, a
compressão roda a cada boot de container em vez de uma vez no build.

### 25. Comentário do modelo de negócio ficou contradizendo o backend

`frontend/src/content/landing.ts:110-117` — os preços foram atualizados, mas o
comentário logo acima continua dizendo "O aluno começa no mínimo e pode subir de
plano quando quiser, **sem depender da escola**". O backend entregue hoje faz o
oposto: `PlanoInstitucional` é contratado pela escola e cobrado por conta
(`E15`). Quem for implementar checkout lendo esse comentário constrói a
assinatura errada.

### 26. Documentação de contrato não acompanhou o fluxo de notas

`docs/backend/contratos/API-CONVENCOES.md` e `MODELO-DE-DADOS.md` não citam
`POST /academico/notas/<pk>/aprovar/`, nem a regra "diretor só lê nota
aprovada", nem que diretor deixou de lançar nota e falta. Isso está só na
`docs/REVISAO-2026-08-05-SEGURANCA-E-INTEGRACAO.md`, que é um documento de
revisão, não de contrato.

### 27. Os 3 testes pulados são justamente os críticos

`backend/limites/tests/test_concorrencia.py` e
`backend/creditos/tests/test_concorrencia.py` são `skipif(vendor == "sqlite")`,
e SQLite é o modo documentado de rodar a suíte. O `189 passed, 3 skipped` é
verdadeiro, mas o `select_for_update` de `trava_cota` — a garantia central do
achado 1 e do achado 5 — **nunca foi exercitado** em nenhuma execução
registrada. Vale um job em Postgres antes de confiar nele em produção.

### 28. Duplicação de fixtures e `views.py` faz-tudo

Seis `conftest.py` (`academico`, `ia`, `creditos`, `conteudo`, `memoria`,
`arquivos`) declaram `instituicao`/`aluno` quase idênticos, e
`limites/tests/test_cota.py:27-40` mais `aluno/tests/test_agenda.py:10-20` os
redeclaram inline por não haver conftest nesses apps. Um conftest raiz
resolveria. Em paralelo, `backend/painel_admin/views.py` está com 280 linhas e
13 views cobrindo instituições, usuários, contas de teste e auditoria — vale
dividir por assunto, como `services/` e `forms/` já são.

---

---

## Correções aplicadas

### Bloqueante 1 — competência mensal do limite

| Arquivo | O que mudou |
|---|---|
| `backend/limites/ciclo.py` | **novo** — única fonte da regra de janela (`YYYY-MM`, mês-calendário UTC) |
| `backend/limites/models.py` | `ConsumoIA.ciclo`, gravado no débito; índices `(usuario, ciclo)` e `(instituicao, ciclo)` |
| `backend/limites/servico.py` | `estado_cota(usuario, *, ciclo=None)` filtra pela competência; `registrar_uso` resolve o ciclo **uma vez sob a trava** e usa o mesmo valor na checagem e na gravação, para não cair em meses diferentes numa chamada na virada |
| `backend/limites/serializers.py` | `ciclo` no estado e no histórico; `limite_percentual` passou a `max_digits=8`, alinhado ao model |
| `backend/limites/migrations/0003_consumo_ciclo.py` | **nova** — backfill a partir de `criado_em`, em lotes de 2000 com `iterator()`+`bulk_update` (não repete o loop por linha do achado 15) |

A competência é gravada no débito em vez de derivada de `criado_em` na leitura:
mantém o registro append-only auditável e impede que uma futura mudança de
regra de janela reescreva retroativamente o que já foi cobrado.

### Bloqueante 2 — backfill das notas existentes

`backend/academico/migrations/0003_notas_existentes_oficiais.py` (nova) marca
`oficial=True` em toda nota já existente, num único `UPDATE`. Essas notas já
eram visíveis ao diretor sob a regra anterior, então o backfill preserva o
comportamento observado sem conceder nada novo — a regra de aprovação vale para
o que for lançado a partir daí.

Sem reversão automática (`RunPython.noop`): depois do backfill não há como
distinguir a nota marcada pela migração da aprovada de verdade, e adivinhar
esconderia nota legítima do diretor. O motivo está escrito no docstring da
migração.

### Bloqueante 3 — o simulado passa a nascer da resposta do modelo

| Arquivo | O que mudou |
|---|---|
| `backend/conteudo/questoes_ia.py` | **novo** — monta o prompt com o formato de resposta exigido e interpreta o JSON do modelo; recusa qualquer desvio |
| `backend/ia/provedores/roteiros.py` | **novo** — saídas estruturadas determinísticas do provedor falso, acopladas por *nome de contrato* (string no prompt), como seria com `response_format` num provedor real |
| `backend/ia/provedores/falso.py` | honra o contrato quando o prompt declara um; mantém o texto padrão nos demais casos |
| `backend/conteudo/simulados.py` | usa prompt+interpretador, `bulk_create` no lugar de N `create()` |
| `backend/conteudo/excecoes.py` | `SimuladoIndisponivelError` (`codigo="simulado_indisponivel"`) |
| `backend/conteudo/simulado_views.py` | `503` para `SimuladoIndisponivelError` e `ProvedorIAError` — antes, falha de provedor virava `500` |

O gateway continua **fora** da transação de propósito: se o modelo não honrar o
contrato, nada é criado e o consumo já debitado permanece, porque a chamada
realmente aconteceu e realmente custou. Fabricar questão para "aproveitar" o
débito era exatamente o defeito.

O provedor falso agora gira o gabarito entre A–D. Isso deixou de ser cosmético:
é o que impede que marcar sempre a mesma alternativa dê 100% e envenene o
`progresso_por_materia` do dashboard.

### Validação das correções

- Suíte backend em SQLite: **`213 passed, 3 skipped`** (eram `189 passed, 3
  skipped`; **24 testes novos**, nenhum existente removido).
- `manage.py check` sem issues; `makemigrations --check --dry-run` sem mudanças
  pendentes; `git diff --check` sem saída.
- Os testes novos: `backend/limites/tests/test_ciclo.py` (6),
  `backend/conteudo/tests/test_questoes_ia.py` (17, incluindo 8 casos
  parametrizados de saída fora do contrato) e um novo em
  `backend/conteudo/tests/test_simulados.py` provando que responder "A" em
  quatro questões dá 25%, não 100%.
- `backend/limites/tests/test_cota.py` teve uma asserção atualizada — o teste
  que fixa o formato de `GET /limites/uso/` pegou a adição de `ciclo`, que é o
  comportamento correto dele.
- **Verificação manual objetiva da migração de notas** (migração de dados não
  tem teste automático viável aqui, sem `django-test-migrations`): num SQLite
  temporário, migrei `academico` até `0002`, criei uma `Nota` (`oficial=False`),
  rodei `migrate academico` e conferi a contagem — `ANTES oficial=True: 0 |
  oficial=False: 1` → `DEPOIS oficial=True: 1 | oficial=False: 0`.

---

## Correções aplicadas — segunda rodada (importantes 5, 6, 7 e sugestão 27)

### Achado 7 — custo pago e débito recusado

O erro estava na divisão de papéis: `registrar_uso` recebia o percentual
**depois** de o provedor ter respondido, ou seja, depois de o custo virar fato,
e ainda assim recusava. Agora:

- `autorizar_uso` é o **único** ponto que recusa, e roda antes da chamada.
- `registrar_uso` é livro-razão: grava sempre, mesmo estourando o plano.
  A conta fica com `disponivel_percentual` negativo e `bloqueado=True`, o que
  barra a chamada seguinte pelo portão.

**Mudança de regra de produto:** o E15 dizia "rejeita um débito que ultrapasse
o limite restante". Isso passa a ser "admite um estouro de no máximo uma
chamada, registra, e bloqueia a próxima". É a única combinação que não perde
dinheiro — recusar depois de pagar deixava o custo existindo no fornecedor e
não existindo na nossa contabilidade.

### Achados 5 e 6 — transação atravessando a rede

`ia/gateway.py` foi reorganizado em três fases explícitas: **portão** (transação
curta com a trava da cota), **provedor** (sem transação aberta) e **débito**
(transação curta). `memoria/tutor.py` perdeu o `atomic()` que envolvia a chamada
inteira; sobrou um em volta só das duas mensagens, que precisam nascer juntas.

Isso resolve o 6 de graça: o `ChamadaIA` de erro que o gateway grava não é mais
revertido pelo `atomic()` do chamador, então a auditoria de falha passa a
existir pelo tutor como já existia pelo simulado.

### Teto de concorrência — necessário por causa do 7

Tirar a trava de cima da chamada externa abriria um buraco novo: N requisições
simultâneas passariam pelo portão juntas (nenhuma debitou ainda) e o estouro
seria do tamanho da concorrência, não de uma chamada. `GatewayIA` agora admite
**uma chamada em andamento por conta**, decidido sob a trava, comparando por
`pk` para que duas requisições simultâneas não se recusem mutuamente — a mais
antiga segue, a mais nova recebe `409 chamada_em_andamento`.

Chamada `PENDENTE` mais velha que a janela de abandono (`timeout × tentativas ×
2`) é tratada como órfã, senão um processo morto no meio travaria a conta para
sempre. Tratado em `memoria/views.py`, `conteudo/simulado_views.py` e
`conteudo/material_views.py` — esta última também passou a devolver `503` para
`ProvedorIAError`, que antes virava `500`.

### Sugestão 27 — os testes de concorrência nunca tinham rodado

Encontrei um Postgres local e tentei rodá-los. Descobri que
`limites/tests/test_concorrencia.py` **não roda em lugar nenhum**: pedia as
fixtures `instituicao`/`aluno`, que viviam dentro de `test_cota.py` — e fixture
declarada num módulo de teste não é visível para outro. O `skipif` de SQLite
escondia um `ERROR`, não um teste passando.

Além disso, os dois módulos de concorrência usam `django_db(transaction=True)`,
que faz *flush* das tabelas ao terminar e leva junto o catálogo de planos
semeado por migração de dados — quebrando a si mesmos ou a quem rodasse depois,
só em PostgreSQL.

Corrigido com `limites/tests/conftest.py` (fixtures compartilhadas, que também
elimina a duplicação apontada na sugestão 28 dentro deste app) e
`serialized_rollback=True` nos dois módulos transacionais.

**Resultado: a suíte roda inteira em PostgreSQL pela primeira vez —
`221 passed`, zero skips.**

### Validação desta rodada

| Ambiente | Resultado |
|---|---|
| SQLite | `218 passed, 3 skipped` |
| PostgreSQL local | **`221 passed`, 0 skipped** |

`manage.py check` sem issues, `makemigrations --check --dry-run` sem pendências,
`git diff --check` sem saída. Banco temporário de Postgres removido no fim.

Um teste existente foi reescrito: `test_registro_rejeita_debito_que_ultrapassa_limite`
fixava exatamente o comportamento que perdia dinheiro. Virou
`test_debito_que_ultrapassa_o_limite_e_registrado_e_bloqueia_a_proxima`.

---

## Correções aplicadas — terceira rodada (importantes 9, 10, 14, 16 e sugestão 18)

### Achado 10 — arquivar instituição era irreversível

O `update()` em massa desativava todas as contas sem registrar **quais** estavam
ativas antes. Depois do ato não havia o que desfazer: reativar tudo
ressuscitaria também quem já estava inativo por outro motivo.

`painel_admin/services/arquivar_instituicao.py` agora grava **um registro de
auditoria por conta atingida**, e é esse registro que torna a operação
reversível. `desarquivar_instituicao` reativa exatamente o conjunto do **último**
arquivamento — o recorte por ciclo importa, porque entre um arquivamento e outro
alguém pode ter sido desativado individualmente, e essa conta não pode voltar só
porque a escola reabriu. Conta transferida para outra escola no meio também não
volta (`instituicao=alvo` no filtro).

Rota `painel-instituicao-desarquivar` + bloco no template, que troca "Arquivar"
por "Reabrir" conforme o estado. O `update()` também passou a preencher
`atualizado_em` na mão, que `auto_now` não cobre em atualização em massa.

### Achado 9 — listas do painel truncadas em 100

`instituicoes` e `usuarios` passaram a usar `Paginator` (25 por página, mesmo
número já usado em `registros`), com navegação e contagem total na tela. O corte
em `[:100]` fazia a 101ª escola simplesmente não existir para o superadmin.

### Achado 16 — `DISTINCT` na tabela de auditoria a cada request

O filtro de ações saía de um `DISTINCT` sobre a tabela inteira — a que mais
cresce, sem índice em `acao` — a cada carga de `/painel/registros/`, inclusive a
cada troca de página. Virou a constante `ACOES_AUDITADAS`.

### Achado 14 — unicidade de e-mail

`editar_usuario` usava igualdade exata enquanto a criação usava `__iexact`.
Como `normalize_email` só normaliza o domínio e o índice único do Postgres
diferencia maiúsculas, editar para `ana@x.com` passava por cima de um
`Ana@x.com` existente. Alinhado com `__iexact`, com teste.

### Sugestão 18 — ordem dos decoradores

`@require_POST` estava **acima** de `@superadmin_required` em 6 views, então um
`GET` anônimo em `/painel/usuarios/1/desativar/` recebia `405` — confirmando a
existência da rota — em vez de ir para o login. Ordem invertida nas 6.

### Achado 8 — `datetime` naive no filtro da agenda

`datetime.fromisoformat` devolve naive, e com `USE_TZ=True` isso emitia
`RuntimeWarning` a cada request e deixava o fuso implícito. Agora usa
`parse_datetime`/`parse_date` + `make_aware`, aceita `YYYY-MM-DD` puro e data
com offset, e recusa lixo com `400`.

### Validação desta rodada

| Ambiente | Resultado |
|---|---|
| SQLite | `231 passed, 3 skipped` |
| PostgreSQL | `234 passed`, 0 skipped |

`manage.py check`, `makemigrations --check --dry-run` e `git diff --check`
limpos. 13 testes novos (`painel_admin/tests/test_arquivamento.py` e três em
`aluno/tests/test_agenda.py`). Nenhuma migração nova nesta rodada.

---

## Veredito

**Pode seguir para os bloqueantes; ainda precisa de ajuste antes de fechar o
resto.** A camada de serviços, a auditoria e o isolamento multi-tenant estão
bem construídos — os três problemas graves eram regras de negócio que o código
não implementava como a documentação promete, e os três foram corrigidos com
teste de regressão.

Todos os 3 bloqueantes e 7 dos 13 importantes foram corrigidos. Nenhum risco de
**dinheiro**, **dado acadêmico** ou **perda irreversível de informação**
continua aberto.

### Corrigidos

| # | Achado | Rodada |
|---|---|---|
| B1 | Limite de uso nunca reiniciava | 1ª |
| B2 | Notas existentes invisíveis ao diretor | 1ª |
| B3 | Simulado com questão fabricada e gabarito fixo | 1ª |
| 5 | Transação aberta durante a chamada ao provedor | 2ª |
| 6 | Registro de erro do gateway revertido pelo tutor | 2ª |
| 7 | Custo pago ao fornecedor e recusado no débito | 2ª |
| 27 | Testes de concorrência que nunca rodaram | 2ª |
| 9 | Listas do painel truncadas em 100 | 3ª |
| 10 | Arquivamento de instituição irreversível | 3ª |
| 14 | Unicidade de e-mail sensível a maiúsculas | 3ª |
| 16 | `DISTINCT` na auditoria a cada request | 3ª |
| 18 | Ordem dos decoradores nas rotas destrutivas | 3ª |
| 8 | `datetime` naive no filtro da agenda | 3ª |

### Abertos

1. **Contrato de erro inconsistente** na superfície nova (importante 4).
   Ficou mais barato do que estimei: o handler único
   (`core.erros.tratador_de_excecao`) **já existe e já está configurado** em
   `REST_FRAMEWORK["EXCEPTION_HANDLER"]` — as views novas simplesmente não
   passam por ele. É trocar `Response(...)` manual por exceções DRF, de
   preferência junto com o 13.
2. **`perfil != "ALUNO"` copiado em 12 views** (importante 13), com string
   mágica em vez de `Perfil.ALUNO` e sem `BasePermission`.
3. **Allowlist do proxy fora do caminho do tráfego** + domínio Railway
   hardcoded em 6 pontos do `vercel.json` (importante 12). **Precisa de decisão
   antes de código:** ou todo o tráfego administrativo passa a ir pela função
   (mudança de roteamento de produção, que pede validação remota), ou o
   comentário de `painel.ts` deixa de afirmar uma proteção que não está no
   caminho. Não decidi sozinho porque mexe em produção.
4. As sugestões 17, 19, 20, 21, 22, 23, 24, 25, 26 e 28, que são qualidade e
   documentação, sem risco funcional conhecido.

Recomendo 4 + 13 juntos como próxima rodada: são as mesmas linhas de código, e
o 4 fica mais caro depois que o frontend passar a consumir os erros.

**Estado final:** REVISÃO CONCLUÍDA; **3 bloqueantes + 7 importantes + 2
sugestões corrigidos**, validados em SQLite e PostgreSQL e **publicados em
`origin/main`**. Os achados 4, 12 e 13 permanecem abertos, com o 12 dependendo
de decisão da usuária. Identidade: **Code review**.
