# Revisão técnica — 2026-08-05 · segurança, integração e painel de superadmin

Plano de correção derivado de um code review da conexão backend↔frontend e do
painel de superadmin (E14). **Ordenado do mais fácil para o mais difícil**, para
ser executado de cima para baixo.

- **Autor da revisão:** agente "Front-End do prisma" (canvas Felixo AI Core).
- **Execução:** agente "Code Review" (retomada autorizada pela usuária em
  2026-08-05).
- **Base revisada:** `main` no commit `4c4e644`, com os commits `a202e16`
  (testes de hierarquia), `2aaca78` (2ª fatia do painel) e `de1447b`
  (allowlist do proxy).
- **Estado deste plano:** *concluído em código e validação local; validação
  remota do deploy permanece pendente por não alterar Railway/Vercel neste
  turno.* O registro final de cada achado está no fim deste documento.

## Como esta revisão foi feita

Nada aqui é leitura de código apenas. Cada achado foi reproduzido antes de ser
escrito:

- Suíte completa rodada: `122 passed, 1 skipped` — a alegação do commit
  `a202e16` **confere**. Só roda com `DATABASE_URL` apontando para SQLite; sem
  isso a suíte tenta o Postgres e dá `118 errors` de conexão.
- Quatro testes descartáveis escritos para provar os achados 5, 6, 7 e 8 — todos
  reproduziram.
- Produção testada ao vivo (`frontend-three-ecru-55.vercel.app`) para os achados
  1 e o diagnóstico de integração.

## Resposta às duas perguntas que originaram a revisão

### O backend já está conectado ao frontend?

**Sim na camada de API, não na jornada do usuário.**

A ponte funciona e foi confirmada ao vivo:

| Verificação | Resultado |
| --- | --- |
| `GET /api/v1/health/` | `200` |
| `POST /api/v1/auth/login/` (senha errada) | `401` com o payload de erro real do Django |
| Allowlist do proxy (`de1447b`) | ativa, rotas fora da lista devolvem 404/405 |

O caminho `vercel.json` → `frontend/api/proxy.ts` → Railway está correto e
seguro. **Mas nenhum usuário consegue concluir um login** por causa do Achado 1:
o redirecionamento pós-login aponta para uma URL que não existe.

### O painel de superadmin está conforme as regras de negócio?

**O painel sim; o sistema em volta não.**

O que está **correto** e foi confirmado:

| Papel | Comportamento verificado | Onde |
| --- | --- | --- |
| Superadmin | Único com acesso a `/painel/`; sem filtro de tenant | `painel_admin/permissoes.py:12` |
| Diretor | Vê toda a instituição, qualquer turma/professor | `academico/notas.py:82-85` |
| Professor | Só as próprias turmas | `academico/notas.py:77-81` |
| Aluno | Só as próprias notas | `academico/notas.py:72-76` |

O que **contradiz** a regra "só o superadmin é cross-tenant": a mesma capacidade
destrutiva do painel existe numa rota REST paralela protegida por `is_staff` em
vez de `is_superuser` (Achado 5). A verificação anterior provou que o painel é
exclusivo do superadmin, mas não perguntou se a mesma capacidade existe em outro
lugar com portão mais fraco — e existe.

---

# Plano de correção (fácil → difícil)

| # | Achado | Severidade | Esforço |
| --- | --- | --- | --- |
| 1 | Login quebrado em produção (caminho relativo) | 🔴 Bloqueante | Trivial |
| 2 | `try/except` no-op em `zerar_creditos` | 🔵 Sugestão | Trivial |
| 3 | `set-cookie` lido com `get()` em vez de `getSetCookie()` | 🔵 Sugestão | Trivial |
| 4 | `GET /notas/` estoura 500 para perfil nulo | 🟠 Importante | Pequeno |
| 5 | `TurmasView` sem validação de perfil | 🟠 Importante | Pequeno |
| 6 | `consultar_notas` ignora `aluno_alvo` para DIRETOR | 🟠 Importante | Pequeno |
| 7 | Motivo em branco aceito em ação destrutiva | 🔵 Sugestão | Pequeno |
| 8 | `is_staff` desativa usuário de qualquer instituição | 🔴 Bloqueante | Médio |
| 9 | Comparações de tenant com `None` | 🔵 Sugestão | Médio |
| 10 | Race condition (TOCTOU) no zerar créditos | 🟠 Importante | Médio-alto |
| 11 | **Fluxo de nota contraria a regra de negócio** (diretor lança nota; vê nota não aprovada; `oficial` é campo morto) | 🔴 Bloqueante | Alto |
| 12 | Lacunas de teste (cross-tenant, diretor no painel, POSTs) | 🟠 Importante | Alto |
| 13 | `IA.md` desatualizado sobre a E14 | 🔵 Sugestão | Fechamento |

> **Por que o bloqueante nº 1 vem primeiro mesmo sendo o mais fácil:** ele é
> uma correção de duas linhas e está afetando usuária real agora. Os dois
> critérios (facilidade e urgência) apontam para o mesmo item, então não há
> conflito de ordenação aqui.

---

## 1. 🔴 Login quebrado em produção — caminho relativo pós-login

**Arquivo:** `frontend/app/login.html:307-308`

### O que está acontecendo

```js
var destinos = {ALUNO: 'aluno.html', PROFESSOR: 'professor.html', DIRETOR: 'diretor.html'};
location.href = destinos[usuario.perfil] || 'index.html';
```

`vercel.json` faz um **rewrite** (não um redirect) de `/entrar` para
`/app/login.html`. Rewrite mantém a URL na barra de endereço como `/entrar`.
Um caminho relativo (`aluno.html`) resolve contra o diretório da URL **atual**,
que é a raiz — não contra `/app/`.

### Cenário concreto (provado ao vivo, em produção, hoje)

| Caminho que o login tenta abrir | Status real |
| --- | --- |
| `/aluno.html` | **404** |
| `/professor.html` | **404** |
| `/diretor.html` | **404** |
| `/app/aluno.html` (o que existe) | 200 |

Todo login bem-sucedido termina em 404. E quando o perfil não bate com nenhuma
das três chaves — caso do superadmin criado em produção, que tem `perfil=None` —
cai no fallback `'index.html'`, que resolve para `/index.html`: **a landing page
pública**. É exatamente o sintoma relatado ("volta pra landing").

### Correção

```js
var destinos = {
  ALUNO: '/app/aluno.html',
  PROFESSOR: '/app/professor.html',
  DIRETOR: '/app/diretor.html',
};
location.href = destinos[usuario.perfil] || '/app/index.html';
```

### Atenção antes de aplicar

`frontend/public/app/login.html` **não existe mais** — só
`frontend/app/login.html`. Como o Vite copia apenas `public/` para `dist/`,
confirme como `dist/app/` está sendo populado no build antes de assumir que
editar um arquivo só é suficiente.

### Como validar

Depois do deploy, `curl -s https://<host>/entrar | grep destinos` deve mostrar
os caminhos absolutos, e um login real deve cair em `/app/<perfil>.html`.

---

## 2. 🔵 `try/except` que não faz nada

**Arquivo:** `backend/painel_admin/services/zerar_creditos.py:24-25`

```python
except AlocacaoSemConfirmacaoError as erro:
    raise AlocacaoSemConfirmacaoError(str(erro)) from erro
```

Captura uma exceção e relança **o mesmo tipo, com a mesma mensagem**. Não
adiciona contexto, não traduz, não registra. É ruído que sugere ao próximo
leitor que existe um tratamento onde não existe.

### Correção

Remover o `try/except` e deixar `return reduzir_alocacao(...)` direto. A
exceção sobe igual, e a view já a captura (`painel_admin/views.py:120`).

---

## 3. 🔵 `set-cookie` lido de forma que quebra com mais de um cookie

**Arquivo:** `frontend/api/proxy.ts`, função `copiarCabecalhos`

```ts
for (const nome of ['cache-control', 'content-type', 'location', 'vary', 'set-cookie']) {
  const valor = resposta.headers.get(nome)
  if (valor) cabecalhos.set(nome, valor)
}
```

`Headers.get('set-cookie')` junta **todos** os cookies numa única string
separada por vírgula. Reenviar isso como um header só faz o navegador
interpretar tudo como um cookie malformado.

### Por que ainda não quebrou

Hoje o backend define **um** cookie por resposta (`refresh_token`, em
`authenticacao/views.py`). O bug é latente: no dia em que entrar um `csrftoken`,
um `sessionid` ou um segundo cookie de auth, o login quebra silenciosamente e o
sintoma não vai apontar para este arquivo.

### Correção

```ts
function copiarCabecalhos(resposta: Response): Headers {
  const cabecalhos = new Headers()
  for (const nome of ['cache-control', 'content-type', 'location', 'vary']) {
    const valor = resposta.headers.get(nome)
    if (valor) cabecalhos.set(nome, valor)
  }
  // set-cookie precisa de tratamento próprio: `get()` junta múltiplos cookies
  // numa string só com vírgula, o que corrompe todos eles.
  for (const cookie of resposta.headers.getSetCookie()) {
    cabecalhos.append('set-cookie', cookie)
  }
  return cabecalhos
}
```

---

## 4. 🟠 `GET /api/v1/academico/notas/` estoura 500 para perfil nulo

**Arquivo:** `backend/academico/views.py:45`

### O que está acontecendo

`consultar_notas` levanta `AcademicoPermissaoError` quando o perfil não é
ALUNO/PROFESSOR/DIRETOR (`academico/notas.py:86`). O `POST` da mesma view trata
essa exceção (linhas 70-71) e o `NotaDetalheView` também (linhas 87-88). **Só o
`GET` não trata.**

Como `perfil` é `null=True` (`contas/models.py:57`) e o superadmin criado em
produção tem `perfil=None`, essa conta recebe um 500 em vez de um 403.

### Cenário concreto (provado)

Superadmin autenticado → `GET /api/v1/academico/notas/` →
`AcademicoPermissaoError: Perfil sem acesso academico.` sobe sem tratamento.

### Correção

```python
def get(self, request):
    try:
        notas = consultar_notas(usuario=request.user).order_by("-criado_em")
    except AcademicoPermissaoError:
        return Response(status=status.HTTP_403_FORBIDDEN)
    paginator = AcademicoPagination()
    pagina = paginator.paginate_queryset(notas, request)
    return paginator.get_paginated_response(NotaSerializer(pagina, many=True).data)
```

---

## 5. 🟠 `TurmasView` não valida perfil: perfil desconhecido vira diretor

**Arquivo:** `backend/academico/views.py:31-35`

### O que está acontecendo

```python
qs = Turma.objects.filter(instituicao_id=request.user.instituicao_id)
if request.user.perfil == "ALUNO":
    qs = qs.filter(...)
elif request.user.perfil == "PROFESSOR":
    qs = qs.filter(professor_responsavel=request.user)
# sem else: qualquer outro perfil recebe a listagem institucional inteira
```

Quem tem `perfil=None` cai fora dos dois ramos e é tratado **exatamente como um
diretor**, silenciosamente.

### Cenário concreto (provado)

O mesmo superadmin que recebe 500 em `/notas/` recebe **200** em `/turmas/`.
Dois modelos de autorização diferentes para o mesmo perfil, no mesmo app.
Combinado com `instituicao_id=None`, o "tenant" vira o balde de usuários órfãos.

### Correção

Espelhar a decisão que `consultar_notas` já toma — negar explicitamente:

```python
elif request.user.perfil != "DIRETOR":
    return Response(status=status.HTTP_403_FORBIDDEN)
```

### Nota de arquitetura

A causa raiz dos achados 4 e 5 é a mesma: **a regra de quem enxerga o quê está
duplicada entre `notas.py` (serviço) e `views.py` (borda)**, e as duas cópias
divergiram. A `CONSTITUICAO-MODULARIDADE.md` do projeto manda regra de negócio
ficar no serviço. Vale considerar extrair um `turmas_visiveis(usuario)` em
`academico/`, análogo a `consultar_notas`, para a view não decidir permissão.

---

## 6. 🟠 `consultar_notas` ignora `aluno_alvo` quando o usuário é DIRETOR

**Arquivo:** `backend/academico/notas.py:82-85`

O ramo PROFESSOR respeita o filtro (linhas 79-80); o ramo DIRETOR não:

```python
if usuario.perfil == "DIRETOR":
    return Nota.objects.filter(aluno__instituicao_id=usuario.instituicao_id)...
    # aluno_alvo é simplesmente descartado
```

### Por que não é falha de segurança hoje

`NotaDetalheView:86` aplica `.filter(pk=pk)` depois, o que salva esse caminho
específico. Mas é contrato inconsistente: qualquer consumidor futuro que passe
`aluno_alvo` para um diretor recebe a instituição inteira de volta. Também é
desperdício — materializa toda a instituição para conferir uma nota.

### Correção

```python
if usuario.perfil == "DIRETOR":
    notas = Nota.objects.filter(aluno__instituicao_id=usuario.instituicao_id)
    if aluno_alvo:
        notas = notas.filter(aluno=aluno_alvo)
    return notas.select_related("disciplina", "turma")
```

---

## 7. 🔵 Motivo só com espaços passa numa ação destrutiva

**Arquivos:** `backend/creditos/alocacao.py:48` (validação) e
`backend/painel_admin/services/zerar_creditos.py`

`reduzir_alocacao` valida `not motivo` — o que rejeita `""` mas **aceita
`"   "`**. Os outros dois pontos destrutivos do painel fazem `.strip()`:

| Ação | Validação | Aceita `"   "`? |
| --- | --- | --- |
| `alterar_perfil` | `motivo.strip()` | Não |
| `desativar_usuario` | `str(motivo or "").strip()` | Não |
| `zerar_creditos` | `not motivo` | **Sim** |

### Cenário concreto (provado)

`zerar_creditos_usuario(..., motivo="   ")` executa e grava
`RegistroDeAuditoria` com `motivo='   '`. Uma ação destrutiva fica registrada
sem justificativa legível — que é justamente o propósito do campo.

### Correção

Padronizar `.strip()` nas três. Em `creditos/alocacao.py`:

```python
motivo = str(motivo or "").strip()
if not confirmado or not motivo:
    raise AlocacaoSemConfirmacaoError(...)
```

---

## 8. 🔴 `is_staff` desativa usuário de qualquer instituição (escalada cross-tenant)

**Arquivos:** `backend/contas/views.py:16-17` e `backend/contas/desativacao.py:17-20`

### O que está acontecendo

Dois portões, os dois abrindo para `is_staff` — que **não** é `is_superuser`:

```python
# contas/views.py — se for is_staff, o filtro de tenant nem é aplicado
if not request.user.is_staff:
    queryset = queryset.filter(instituicao_id=request.user.instituicao_id)

# contas/desativacao.py — is_staff curto-circuita TODA a checagem de permissão
if not ator.is_staff and (
    ator.perfil != "DIRETOR" or ator.instituicao_id != alvo.instituicao_id
):
    raise DesativacaoNegada(...)
```

`DesativarUsuarioView` exige apenas `IsAuthenticated`. E `is_staff` é um booleano
comum, marcável pelo Django Admin — o próprio arquivo de testes do painel cria um
professor com `is_staff=True`.

### Cenário concreto (provado)

Professor da Escola A com `is_staff=True` faz
`POST /api/v1/contas/usuarios/<pk_do_diretor_da_escola_B>/desativar/` →
**`HTTP 204`**, e o diretor da Escola B fica com `ativo=False`.

Isto é o oposto direto da regra de negócio verificada. O painel exige
`is_superuser` e existe até um teste provando que um staff não entra lá
(`test_staff_nao_superadmin_nao_acessa_painel`) — mas a rota REST ao lado entrega
poder destrutivo cross-tenant para o mesmo usuário barrado no painel.

### Correção

Trocar `is_staff` por `is_superuser` nos dois pontos e transformar o
short-circuit numa regra explícita e legível:

```python
# contas/views.py
if not request.user.is_superuser:
    queryset = queryset.filter(instituicao_id=request.user.instituicao_id)

# contas/desativacao.py — quem pode desativar quem, dito de forma afirmativa
def _pode_desativar(ator, alvo):
    if ator.is_superuser:            # único papel cross-tenant
        return True
    return (
        ator.perfil == "DIRETOR"
        and ator.instituicao_id is not None
        and ator.instituicao_id == alvo.instituicao_id
    )

if not _pode_desativar(ator, alvo):
    raise DesativacaoNegada("Usuario sem permissao para desativar este usuario.")
```

A cláusula `instituicao_id is not None` já resolve o Achado 9 para este caminho.

### Testes obrigatórios junto da correção

1. Staff não-superuser **não** desativa usuário de outra instituição (403/404).
2. Staff não-superuser **não** desativa usuário da própria instituição.
3. Diretor desativa alguém da própria instituição (segue funcionando).
4. Diretor **não** desativa alguém de outra instituição.
5. Superadmin desativa cross-tenant (segue funcionando).

---

## 9. 🔵 Comparações de tenant tratam `None == None` como "mesma instituição"

**Arquivo:** `backend/academico/notas.py:70` (e o padrão se repete)

```python
if aluno_alvo and aluno_alvo.instituicao_id != usuario.instituicao_id:
    raise AcademicoPermissaoError(...)
```

`instituicao` é `null=True` (`contas/models.py:51-54`). Com os dois lados `None`,
`None != None` é falso e a checagem **passa** — dois usuários órfãos são
considerados do mesmo tenant. O mesmo vale para o filtro do diretor
(`aluno__instituicao_id=usuario.instituicao_id` com `None` casa todos os órfãos).

### Correção

Tratar tenant nulo como ausência de acesso, não como um tenant:

```python
if usuario.instituicao_id is None:
    raise AcademicoPermissaoError("Usuario sem instituicao.", codigo="sem_instituicao")
```

no topo de `consultar_notas`, antes dos ramos por perfil.

### Alternativa estrutural (registrar como decisão)

Se a intenção é que **todo** usuário do domínio acadêmico tenha instituição,
o campo talvez devesse ser `null=False` com o superadmin modelado fora desse
domínio. Isso é migração + decisão de modelagem — vale discutir antes, não
mudar de afogadilho.

---

## 10. 🟠 Race condition (TOCTOU) ao zerar créditos

**Arquivo:** `backend/painel_admin/services/zerar_creditos.py:12-16`

```python
saldo = saldo_usuario(alvo.pk)                   # lê fora de qualquer transação
if saldo <= 0:
    raise SaldoJaZeradoError(...)
return reduzir_alocacao(quantidade=saldo, ...)   # grava um valor possivelmente obsoleto
```

Sem `@transaction.atomic` (o `alterar_perfil` ao lado tem) e sem
`select_for_update`. Entre a leitura e a escrita, o saldo pode mudar.

### Cenário concreto

O produto debita crédito após **cada** resposta de IA bem-sucedida — débito
concorrente é o caso normal, não a exceção:

1. Superadmin abre a tela; `saldo_usuario` lê **100**.
2. O aluno faz uma pergunta ao tutor; débito de **30** entra. Saldo real: 70.
3. O serviço grava `DEBITO 100` → **saldo final: −30**.

Nada no ledger impede saldo negativo, e `saldo` é derivado por soma
(`creditos/saldo.py`), então o valor negativo simplesmente passa a existir.

### Correção aplicada

Ler e gravar dentro da mesma transação, usando a mesma linha de controle que o
consumo de IA trava:

```python
with trava_saldo(alvo):
    saldo = saldo_usuario(alvo.pk)
    if saldo <= 0:
        raise SaldoJaZeradoError("Usuario ja esta com saldo zerado.")
    return reduzir_alocacao(..., quantidade=saldo, ...)
```

`trava_saldo` serializa a leitura do saldo com o débito de IA e usa
`TravaSaldoUsuario`, inclusive quando ainda não há lançamentos para travar.

### Atenção

`select_for_update` **não funciona em SQLite** — a suíte roda em SQLite hoje.
Já existe `backend/creditos/tests/test_concorrencia.py` no repositório: seguir
o padrão que ele já usa para esse tipo de teste, em vez de inventar outro.

---

## 11. 🔴 O fluxo de notas contraria a regra de negócio

**Arquivos:** `backend/academico/notas.py`, `backend/academico/views.py`,
`backend/academico/models.py:77`

### A regra, dita pela dona do produto (2026-08-05)

> "Diretor não lança nota nenhuma, notas ficam entre alunos e professores, o
> diretor só vê as notas dos alunos revisadas e aprovadas pelo professor."

Ou seja, o ciclo de vida de uma nota tem três papéis bem separados: **professor
lança e aprova**, **aluno vê a própria**, **diretor só lê o que já foi
aprovado**.

### O que o código faz hoje

| A regra pede | O código faz | Onde |
| --- | --- | --- |
| Diretor não lança nota | **Permite** DIRETOR lançar | `views.py:51` (`perfil not in {"PROFESSOR", "DIRETOR"}`) |
| Diretor não lança falta | **Permite** DIRETOR lançar | `views.py:96` |
| — | Diretor ainda **pula a checagem de matrícula** que o professor sofre | `notas.py:97-98` |
| Diretor só vê nota aprovada | Devolve **todas** as notas da escola, sem olhar `oficial` | `notas.py:82-88` |
| Professor aprova a nota | **Não existe** | — |

### O achado central: `oficial` é um campo morto

`Nota.oficial` (`models.py:77`, `default=False`) é exatamente o "revisada e
aprovada pelo professor" que a regra pede. E a especificação da etapa já previa
isso — `docs/backend/etapas/E09-academico.md`:

> "Nota gerada por IA | Nasce como rascunho. So vira oficial por acao do
> professor (E10)."

Mas o campo é **declarado, exposto no serializer como read-only, e nunca lido
nem escrito por nenhuma linha de código do repositório**. Não há endpoint,
serviço ou ação que marque uma nota como oficial.

Existe um fluxo de aprovação completo e bem feito — `oficializar_prova`, com
confirmação, motivo obrigatório e auditoria (`conteudo/servico.py:54`) — mas ele
é para **Prova**, no app `conteudo`. O equivalente para **Nota** nunca foi
construído.

### Consequência prática

**Toda nota do sistema é `oficial=False` hoje.** Por isso a correção não pode
ser só adicionar o filtro na consulta do diretor: sem a ação de aprovar, a tela
dele passaria a mostrar zero notas. Corrigir a leitura sem construir a escrita
troca um comportamento errado por outro.

### Por que isso passou despercebido

A verificação de hierarquia feita antes desta revisão deu como **correto** o
comportamento do diretor ("enxerga toda a instituição, notas de qualquer aluno
da escola") e adicionou 5 testes que o congelam. Os testes são bem escritos —
mas cristalizam um comportamento que contraria a regra de negócio. É o risco de
validar a implementação contra si mesma em vez de contra a regra: tudo passa, e
o desvio fica mais difícil de remover depois.

### Correção (3 partes, nesta ordem)

**(a) Tirar o diretor da escrita** — `views.py`, `NotasView.post` e
`FaltasView.post` passam a aceitar só `PROFESSOR`; `_validar_lancamento` perde o
`return` antecipado do diretor.

**(b) Construir a aprovação da nota** — concluído em `aprovar_nota` e
`POST /api/v1/academico/notas/<pk>/aprovar/`, no padrão que `oficializar_prova`
já estabeleceu: só o professor responsável pela turma aprova, exige confirmação
e motivo, grava `RegistroDeAuditoria`, e uma nota já oficial não é reaprovada.
Nota oficial tem a aprovação revogada quando seu valor é alterado e exige nova
revisão explícita. A operação usa lock transacional e autoriza o tenant antes de
consultar `oficial`, evitando revelar estado cross-tenant.

**(c) Filtrar a leitura do diretor** — o ramo DIRETOR de `consultar_notas` passa
a devolver só `oficial=True`. Aluno e professor continuam vendo rascunho (é o
trabalho em andamento deles).

### Testes obrigatórios

1. Diretor recebe 403 ao tentar lançar nota; 403 ao tentar lançar falta.
2. Professor aprova a própria nota; nota vira `oficial=True` e gera auditoria.
3. Professor não aprova nota de turma de outro professor.
4. Aprovar sem confirmação/motivo é recusado.
5. Diretor vê nota aprovada e **não** vê rascunho.
6. Aluno e professor continuam vendo o rascunho.

### Decisão registrada e aplicada

Documentar primeiro, implementar em seguida — decisão da dona do produto em
2026-08-05. A implementação foi validada por testes de serviço e endpoint.

---

## 12. 🟠 Lacunas de teste nos pontos que a verificação alegou provar

Os 5 testes de `a202e16` são bem escritos — testam comportamento, não
implementação, e rodam de fato. As lacunas não são de qualidade, são de
**cobertura do lado negativo**:

### 12a. Nenhum teste usava duas instituições

Todos os 5 compartilham a fixture `instituicao`. A afirmação central da
verificação — "diretor vê a instituição inteira; superadmin é o único sem filtro
de tenant" — nunca é provada pelo lado que importa: **falta "diretor da Escola A
não vê nota da Escola B"**.

Num produto B2B multi-tenant esse é o teste mais importante do conjunto, e é o
que não existe. (Existe `test_professor_de_outra_instituicao_recebe_404` para
professor; o equivalente para diretor não.)

### 12b. Nenhum teste de que DIRETOR não acessava o painel

Justamente a regra questionada. Há teste com ALUNO (`test_painel_exige_superadmin`)
e com PROFESSOR + `is_staff` (`test_staff_nao_superadmin_nao_acessa_painel`),
mas **não com DIRETOR** — o perfil com mais poder abaixo do superadmin.

### 12c. As três ações destrutivas não tinham teste de autorização

`usuario_perfil`, `usuario_desativar` e `usuario_zerar_creditos` só têm testes de
caminho feliz e de validação. Os testes de 403 cobrem apenas os `GET` de
dashboard e registros. Os decoradores estão corretos hoje — mas nada trava se
alguém remover um `@superadmin_required` numa refatoração.

### Correção

Os testes foram adicionados em `academico/tests/test_revisao_notas.py`,
`academico/tests/test_views.py`, `contas/tests/test_admin_onboarding.py` e
`painel_admin/tests/test_painel_superadmin.py`, incluindo o lado negativo de
tenant, o diretor fora do painel e as três ações destrutivas.

---

## 13. 🔵 `IA.md` desatualizado sobre a E14

`IA.md:549` ainda registra o painel como:

> "Primeira fatia implementada… `4 passed`… Estado: **AGUARDANDO DECISÃO**"

Mas a 2ª fatia (registros de auditoria, zerar créditos, desativar usuário) foi
entregue em `2aaca78` e a suíte do painel foi a **14 testes**. O fechamento
existe apenas em `docs/CANVAS-NOTAS.md` e na mensagem de commit — o `IA.md`, que
é o contexto operacional do projeto, ficou para trás. Outro agente já citou "o
encerramento da E14 registrado por 'Painel do prisma'" referindo-se a um registro
que não está lá.

### Correção

Fechar a entrada da E14 no `IA.md`, registrando o resultado desta revisão, o
que foi corrigido, o que ficou pendente e por quê.

---

# Registro final da execução — Code Review

- [x] 1–3: login pós-rewrite com caminhos absolutos, remoção do `try/except`
  no-op e encaminhamento individual de múltiplos `set-cookie`.
- [x] 4–7: respostas seguras para perfil sem acesso, validação explícita de
  perfil em turmas, filtro de `aluno_alvo` para diretor e motivo com `strip()`.
- [x] 8–10: superadmin como único escopo cross-tenant da desativação, tenant
  nulo negado e zeramento serializado com consumo de IA.
- [x] 11: diretor retirado da escrita acadêmica, aprovação de nota criada,
  leitura do diretor filtrada por `oficial=True` e alteração de nota oficial
  exigindo nova revisão.
- [x] 12: testes de autorização, cross-tenant, painel, endpoints e
  concorrência adicionados ou ajustados.
- [x] 13: `IA.md` atualizado com decisão, correções e evidências.

Validação final observada: `142 passed, 2 skipped` no backend com SQLite;
`manage.py check` e `makemigrations --check --dry-run --noinput` sem mudanças;
frontend `npm test` (2 testes), `npm run lint` e `npm run build` concluídos;
`git diff --check` sem saída; `Headers.getSetCookie` disponível na versão Node
instalada e o build contém os destinos `/app/*.html`.

## Limites restantes após a execução

1. O deploy remoto de frontend/backend não foi disparado neste turno. O build
   local confirma os caminhos em `dist/app/login.html`, mas o login em produção
   precisa ser revalidado após o próximo deploy autorizado.
2. Os testes de threads PostgreSQL foram pulados localmente porque o ambiente
   usa SQLite; o teste existente de concorrência e o novo teste de zeramento
   devem ser executados contra PostgreSQL antes de release.
3. A variável `PRISMA_API_ORIGIN` ainda tem pendência operacional registrada no
   `IA.md`; o fallback público permanece apenas para não interromper a produção.

**Estado final:** CONCLUÍDO localmente; sem bloqueio de código. Aguardando
somente validação remota/configuração operacional fora deste turno.

## 14. Login administrativo autenticava, mas não chegava ao painel

### Diagnóstico

A produção retornou sucesso no login e carregou `/auth/eu/`, mas a conta
administrativa tinha `perfil=null`. O frontend só conhecia os destinos
acadêmicos e exibia “Esta conta não tem perfil...”. Além disso, o endpoint JWT
não criava a sessão Django exigida por `/painel/`, e a Vercel não encaminhava as
rotas HTML do painel.

### Correção aplicada

- `LoginView` cria sessão Django somente quando o usuário autenticado é
  `is_superuser`; contas acadêmicas continuam apenas no fluxo JWT.
- `EuSerializer` expõe `is_superuser` e `login.html` encaminha esse usuário para
  `/painel/`.
- `frontend/api/painel.ts` implementa uma ponte same-origin separada, com
  allowlist de prefixo/método para `/painel/`, `/backoffice/` e `/static/`,
  preservando cookies, redirects e cabeçalhos necessários.
- `vercel.json` publica os rewrites do painel. A API continua com sua própria
  allowlist, sem transformar o proxy em encaminhamento genérico.
- `frontend/README.md` registra a exigência operacional de incluir a origem
  pública da Vercel em `DJANGO_CSRF_TRUSTED_ORIGINS` no ambiente Django.

### Validação observada

- `DATABASE_URL=sqlite:///local-test.sqlite3 .venv/bin/pytest -q`
  → `142 passed, 2 skipped`.
- `authenticacao/tests.py` → `11 passed`, incluindo criação de sessão para
  superadmin e ausência de sessão administrativa para usuário acadêmico.
- `manage.py check` e `makemigrations --check --dry-run --noinput` sem erros.
- `npm run lint` e `npm run build` concluídos.
- JSON de `vercel.json` válido; bundle do proxy testado com cenários de rota
  fora da allowlist (404), método inválido (405) e encaminhamento válido.
- `git diff --check` sem saída.

### Limite operacional

Não houve deploy da alteração neste turno. Para o login funcionar na URL
publicada, ainda é necessário publicar frontend/backend e configurar
`DJANGO_CSRF_TRUSTED_ORIGINS` com a origem pública da Vercel; depois disso, o
fluxo deve ser validado remotamente. A senha exibida na captura deve ser
rotacionada.

**Estado final:** CONCLUÍDO localmente; aguardando deploy/configuração
operacional. Identidade: **Code Review**.

## 15. Correção do 404 publicado em `/painel/`

Após a publicação do fluxo administrativo, a URL `/painel/` retornou 404 da
Vercel. A chamada direta ao proxy (`/api/painel?path=painel/`) já retornava
200, isolando o defeito no rewrite: `/painel/:path*` não cobria a rota com a
barra final nesse projeto.

Foram adicionados rewrites explícitos para `/painel/` e `/backoffice/` no
`frontend/vercel.json`. O commit `ce58c92` foi publicado em `origin/main`.
Validação remota após o deploy: `GET
https://frontend-three-ecru-55.vercel.app/painel/` → `200`, com HTML da tela
de login do Django; o proxy direto continuou retornando `200`.

Não foi realizado login manual com a senha visível na captura. O usuário deve
rotacionar essa senha e testar novamente; as ações POST do painel também
dependem de `DJANGO_CSRF_TRUSTED_ORIGINS` conter a origem pública da Vercel.

**Estado final:** CONCLUÍDO; rota publicada e aguardando somente teste manual
autenticado. Identidade: **Code Review**.

## 16. Subrotas do painel com barra final

O 404 restante apareceu em `/painel/usuarios/` e `/painel/registros/`. A
Vercel encaminhava a variante sem barra, mas o Django redirecionava para a
variante canônica com barra e o segundo request não tinha rewrite.

O commit `78d260b` adicionou os padrões `/painel/:path*/` e
`/backoffice/:path*/`, foi publicado em `origin/main` e validado remotamente:

- `/painel/usuarios/` → `302` para o login quando sem sessão;
- `/painel/registros/` → `302` para o login quando sem sessão;
- `/backoffice/login/` → `200`;
- `/static/admin/css/base.css` → `200`.

O `302` é o comportamento esperado para a chamada sem cookie; após autenticar
no fluxo do superadmin, as mesmas subrotas devem entregar o painel. Não foi
enviada a senha exibida na captura.

**Estado final:** CONCLUÍDO; subrotas publicadas e aguardando somente teste
manual autenticado. Identidade: **Code Review**.

## 17. Instituições e contas de teste no painel do superadmin

### Decisão de fluxo de login

O superusuário não deve ser tratado como aluno, professor ou diretor: ele é a
conta de controle cross-tenant da plataforma. Por isso, o login o encaminha ao
`/painel/`. As telas acadêmicas desenvolvidas pelo André são acessadas com uma
conta de teste criada para o perfil correspondente. Isso evita que uma conta
sem instituição seja mascarada como usuário acadêmico e mantém a separação
entre control plane e produto.

### Entrega

- `/painel/instituicoes/` cria instituição com documento único e crédito
  inicial opcional;
- `/painel/contas-teste/` cria conta ativa vinculada a instituição ativa, com
  perfil `ALUNO`, `PROFESSOR` ou `DIRETOR`;
- ambas as operações são exclusivas do superadmin, usam serviço transacional e
  registram `RegistroDeAuditoria`;
- contas de teste têm senha armazenada somente como hash e recebem
  `is_staff=False` e `is_superuser=False` explicitamente;
- duplicidade, senha fraca, perfil inválido e instituição inativa são
  rejeitados sem criação parcial.

### Validação observada

- `DATABASE_URL=sqlite:///local-test.sqlite3 .venv/bin/pytest -q
  painel_admin/tests/test_painel_superadmin.py` → `21 passed`;
- `manage.py check` → nenhum problema;
- `makemigrations --check --dry-run` → nenhuma mudança;
- `git diff --check` → sem saída.

**Estado final:** CONCLUÍDO localmente no commit `2a45e81`; aguardando apenas
deploy e teste manual autenticado. Identidade: **Code Review**.

## 18. Publicação do onboarding administrativo

Os commits `2a45e81` e `7aaaa11` foram publicados em `origin/main`. O Railway
concluiu o deployment da API com status `SUCCESS` no deployment
`75ac6e3d-2ba6-414b-afdc-07a6803e69c3`; o Postgres continuou saudável.

Validação pública observada:

- `/painel/instituicoes/` → `302` para o login sem sessão;
- `/painel/contas-teste/` → `302` para o login sem sessão;
- `/api/v1/health/` → `200`.

**Estado final:** CONCLUÍDO e publicado; aguardando somente teste manual
autenticado. Identidade: **Code Review**.

## 19. Tier mantenedor Vitis Souls e governança cross-tenant

### Decisão

Foi criado um tier técnico separado dos perfis acadêmicos. A instituição
`VITIS_SOULS` é uma mantenedora interna da empresa e não exige CPF/CNPJ. Toda
conta superusuária deve usar o perfil `MANTENEDOR` e pertencer a essa
instituição; a migração `0007_mantenedora_vitis_souls` corrige os superusuários
existentes.

O painel cross-tenant exige quatro condições: conta ativa, superusuário,
perfil `MANTENEDOR` e vínculo com a Vitis Souls. O campo `is_staff`, sozinho,
não concede esse acesso. Instituições escolares e contas de outras escolas
podem ser monitoradas, criadas, editadas e desativadas pelo painel. A operação
chamada de “apagar” é arquivamento lógico com confirmação, motivo, auditoria e
preservação de dados; a exclusão física foi bloqueada no Admin completo.

### Validação observada

- `DATABASE_URL=sqlite:///local-test.sqlite3 .venv/bin/python manage.py check`
  → nenhum problema;
- `DATABASE_URL=sqlite:///local-test.sqlite3 .venv/bin/python manage.py
  makemigrations --check --dry-run` → nenhuma mudança;
- testes focados de onboarding e painel → `45 passed`;
- suíte completa do backend → `156 passed, 2 skipped`;
- `git diff --check` → sem saída.

**Estado final:** CONCLUÍDO localmente; publicação e validação remota serão
registradas após o push. Identidade: **Code Review**.
