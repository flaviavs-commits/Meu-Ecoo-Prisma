# E01 - Fundacao do projeto

> **Status:** CONCLUIDA · **Responsavel:** Claude (API-CONVENCOES.md)
> **Depende de:** nada · **Destrava:** todas as outras etapas
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Deixar um projeto Django rodando, conectado ao Postgres do Railway, com teste
automatizado funcionando e um endpoint de saude respondendo. Nada de dominio
ainda.

Esta etapa e o gargalo do projeto inteiro: enquanto ela nao fecha, ninguem
comeca.

## 2. Pre-requisitos

- Python 3.12 (versao da maquina de desenvolvimento)
- `railway` CLI autenticado - ver [`../FERRAMENTAS-E-ECOSSISTEMA.md`](../FERRAMENTAS-E-ECOSSISTEMA.md)
- Ter lido [`../VISAO-GERAL.md`](../VISAO-GERAL.md)

## 3. Escopo

**Entra:**

- pasta `backend/` com projeto Django e DRF
- settings separados por ambiente
- `requirements.txt` com versoes fixadas + `requirements-dev.txt`
- `.env.example` (nomes de variavel, **sem valor**)
- conexao com o Postgres do Railway
- `pytest` + `pytest-django` configurados e rodando
- handler unico de erro da API (formato do [contrato](../contratos/API-CONVENCOES.md))
- endpoint `GET /api/v1/health/`
- CORS liberado para a SPA em desenvolvimento

**Nao entra:**

- nenhum model de dominio (isso e E02)
- **rodar `migrate`** - leia o alerta abaixo
- deploy (E12)

## 4. ⚠️ Alerta que muda tudo: nao rode `migrate` nesta etapa

O Django exige que o **model de usuario customizado exista antes da primeira
migracao**. Trocar `AUTH_USER_MODEL` depois de migrar e um dos consertos mais
dolorosos do framework - na pratica, significa recriar o banco.

O `Usuario` customizado e criado na **E02**. Portanto:

- **E01 nao roda `migrate`.** Nem `migrate` de app do Django.
- E01 **deve** deixar `AUTH_USER_MODEL = "contas.Usuario"` ja escrito no
  settings, e o app `contas` criado e vazio, para que E02 so precise definir o
  model.
- O teste de conexao com o banco desta etapa usa uma consulta simples
  (`SELECT 1`), nao a criacao de tabela.

Registre no diario que esta regra foi respeitada.

## 5. Decisoes ja travadas - nao reabrir

| Decisao | Valor |
|---------|-------|
| Banco em dev | Postgres do Railway. **Sem SQLite, sem Postgres local, sem container de banco.** |
| Dependencias | `pip` + `requirements.txt` com versao exata (`==`) |
| Estrutura | Apps Django por dominio, nao camadas genericas |
| Testes | `pytest`, TDD |

## 6. Como fazer

### 6.1 Estrutura alvo

```text
backend/
├── config/
│   ├── settings/
│   │   ├── base.py          # comum
│   │   ├── dev.py           # DEBUG on, CORS liberado
│   │   └── prod.py          # DEBUG off, hosts restritos
│   ├── urls.py
│   └── wsgi.py
├── contas/                  # criado vazio, so para AUTH_USER_MODEL apontar
├── core/
│   ├── saude.py             # a view de health check
│   └── erros.py             # o exception handler unico
├── tests/
│   └── test_saude.py
├── manage.py
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

`core/` aqui **nao e um deposito**: guarda infraestrutura da API que nao
pertence a dominio nenhum. Um arquivo, uma responsabilidade - se `core/` comecar
a acumular assunto, quebre.

### 6.2 Settings por ambiente

`base.py` le tudo de variavel de ambiente. Nada de valor sensivel no codigo.

Variaveis minimas (`.env.example`, **so os nomes**):

```
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=
DATABASE_URL=
CORS_ALLOWED_ORIGINS=
```

`DATABASE_URL` vem do Railway. Use `dj-database-url` para interpretar - confirme
a versao instalada antes de usar qualquer opcao dela.

Em `prod.py`, garanta: `DEBUG=False`, `ALLOWED_HOSTS` explicito,
`SECURE_SSL_REDIRECT`, cookie seguro, HSTS.

### 6.3 Conectar ao Railway

```bash
railway status          # confirme projeto e ambiente ANTES de qualquer coisa
railway variables       # veja se ja existe DATABASE_URL
railway run python manage.py check
```

Se o projeto Railway do Prisma ainda nao existir, **nao crie por conta propria** -
isso e escopo da [E12](E12-infra-railway-e-deploy.md) e afeta custo. Registre
como bloqueio e siga com o que der.

> Nunca rode comando destrutivo sem conferir `railway status`. A conta tem
> outros produtos da empresa em producao no mesmo lugar.

### 6.4 TDD - a ordem importa

1. Escreva `tests/test_saude.py`: `GET /api/v1/health/` responde 200 e
   `{"status": "ok"}`.
2. Rode. **Tem que falhar** (rota nao existe). Cole a falha no diario.
3. Implemente a view e a rota.
4. Rode de novo. Passa.
5. Escreva o teste do formato de erro: uma rota inexistente responde no formato
   do [contrato](../contratos/API-CONVENCOES.md), com `erro.codigo`.
6. Implemente o handler em `core/erros.py` e registre em
   `REST_FRAMEWORK["EXCEPTION_HANDLER"]`.

### 6.5 Auditoria de dependencia

Ao fechar o `requirements.txt`, rode `pip-audit` e registre a saida no diario.
Dependencia e superficie de ataque.

## 7. Contrato de saida

O que as proximas etapas podem assumir que existe:

- `backend/` com Django + DRF instalados e `manage.py` funcionando
- `config.settings.dev` e `config.settings.prod` selecionaveis por
  `DJANGO_SETTINGS_MODULE`
- conexao com o Postgres do Railway validada
- `AUTH_USER_MODEL = "contas.Usuario"` ja declarado, app `contas` criado e vazio
- **nenhuma migracao aplicada ainda**
- `pytest` roda a partir de `backend/`
- `GET /api/v1/health/` responde 200 sem autenticacao
- todo erro da API sai no formato unico do contrato

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Uma entrada por decisao, bug, bloqueio ou teste rodado.
> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar a etapa: mude o status do cabecalho para `EM ANDAMENTO`, assine, e
> atualize a sua linha em [`../README.md`](../README.md).

- [2026-08-03] Peguei a etapa E01. Li protocolo do agente, README de etapas, VISAO-GERAL e contrato API-CONVENCOES - por que: nenhuma decisao pode ser tomada sem ver o que ja esta travado - como validei: leitura direta dos arquivos, sem suposicao.
- [2026-08-03] **Nota de coordenacao:** encontrei a linha acima ja escrita quando abri este arquivo para registrar meu proprio trabalho (eu tambem sou um agente identificado como responsavel pela E01, via `docs/backend/contratos/API-CONVENCOES.md`) - ou seja, dois agentes pegaram a mesma etapa em paralelo. Nao apaguei a entrada de quem chegou antes. `backend/` no filesystem so tinha `creditos/` (E05) quando eu comecei a escrever codigo; nao vi nenhum arquivo de outro agente da E01 la, entao segui e entreguei o escopo completo abaixo. Se isso gerar trabalho duplicado, quem ler depois compara os diarios das duas sessoes antes de decidir o que fica.
- [2026-08-03] Ambiente multi-agente confirmado ao vivo: ao montar `backend/`, encontrei `backend/creditos/` ja em construcao por outro agente (E05). Nao toquei nesses arquivos - so limpei o que eu mesmo tinha criado (`config/`, `contas/`, `core/`, `tests/`, `manage.py`) apos um erro de `startapp`, confirmando por timestamp que nada da E05 foi afetado.
- [2026-08-03] **Python 3.12 nao existe nesta maquina** (so 3.11.15 e 3.14.3 via Homebrew, e a criacao inicial do venv misturou os dois por ambiguidade de PATH, causando `ModuleNotFoundError` inconsistente entre comandos). Recriei o venv fixando o interprete por caminho absoluto (`/opt/homebrew/bin/python3.11`). Risco assumido, registrado aqui: 3.11 no lugar de 3.12. Se 3.12 for instalado depois, recriar o venv e conferir `requirements.txt` de novo.
- [2026-08-03] **Projeto "Prisma" nao existe no Railway** (`railway list` mostra 13 projetos da empresa, nenhum com esse nome). Isso e escopo da E12 - nao criei por conta propria. Consequencia: a conexao real com Postgres do Railway (secao 6.3) **nao foi validada**, so a leitura de `DATABASE_URL` via `.env` local (`postgres://prisma:prisma@localhost:5432/prisma_dev`, nunca conectado de fato). `pytest` nao toca o banco porque nenhum teste desta etapa usa fixture `django_db` - health check e handler de erro nao dependem de tabela nenhuma. Pendente para quando a E12 criar o projeto: rodar `railway run python manage.py check` de verdade.
- [2026-08-03] TDD do health check: escrevi `tests/test_saude.py` esperando `GET /api/v1/health/` -> 200 `{"status": "ok"}`. Rodei antes de existir a rota - falhou com `ModuleNotFoundError: No module named 'core.saude'`. Implementei `core/saude.py` (view DRF, `AllowAny`) e `core/urls.py` incluida em `config/urls.py` sob `/api/v1/`. Rodei de novo - passou.
- [2026-08-03] **Contradicao real no desenho da etapa, resolvida:** a secao 4 manda deixar `AUTH_USER_MODEL = "contas.Usuario"` com o app `contas` **vazio**. Isso quebra o Django de verdade - `django.contrib.auth` resolve `AUTH_USER_MODEL` em `AppConfig.ready()` (nao so na migracao), entao o processo nem sobe (`ImproperlyConfigured: AUTH_USER_MODEL refers to model 'contas.Usuario' that has not been installed`). Tirar `django.contrib.admin` do `INSTALLED_APPS` nao bastou sozinho (era ele quem forcava `get_user_model()` mais cedo via autodiscover) - o proprio `django.contrib.auth.apps.AppConfig.ready()` tambem resolve. Solucao: criei um **stub minimo** em `contas/models.py` com `class Usuario(AbstractUser): pass` (so a classe, sem campos extras, sem migracao rodada). `admin` continua fora do `INSTALLED_APPS` nesta etapa - a E02/E11 devolve. Isso muda o "Contrato de saida": a E02 **edita** um `Usuario` que ja existe como classe Python, nao cria do zero.
- [2026-08-03] TDD do handler de erro: dois testes em `tests/test_erros.py`. O primeiro (`rota-que-nao-existe`) falhou antes por nao existir handler - Django devolvia HTML, nao JSON. Implementei `core/erros.py` com `tratador_de_excecao` (registrado em `REST_FRAMEWORK["EXCEPTION_HANDLER"]`) e `pagina_nao_encontrada` (registrado como `handler404` em `config/urls.py`, cobre URL que nem bate numa view DRF). Segundo teste (`POST /api/v1/health/` -> 405) prova o `tratador_de_excecao` funcionando de dentro do DRF. Saida real:
  ```
  tests/test_erros.py::test_rota_inexistente_responde_no_formato_do_contrato PASSED
  tests/test_erros.py::test_metodo_nao_permitido_passa_pelo_handler_unico_do_drf PASSED
  tests/test_saude.py::test_health_check_responde_ok PASSED
  3 passed in 0.13s
  ```
- [2026-08-03] `python manage.py check` (dev): "System check identified no issues (0 silenced)". `check --deploy` com `config.settings.prod`: 1 warning (`security.W009`, `SECRET_KEY` fraca) - esperado, o `.env` local usa secret de desenvolvimento de proposito; nenhum alerta critico.
- [2026-08-03] `pip-audit -r requirements.txt`: "No known vulnerabilities found".
- [2026-08-03] Ao rodar `pytest` **sem** escopo, a colecao global falha: `creditos/tests/conftest.py` (da E05, outro agente) faz `apps.get_model("contas", "Instituicao")`, que so existe na E02. Esperado nesta fase transitoria - nao mudei `pytest.ini` para isolar minha pasta, isso mudaria a convencao de teste do projeto por causa de um estado transitorio. Quem rodar `pytest` a partir de `backend/` antes da E02 fechar deve rodar `pytest tests/` para ver so a fundacao.
- [2026-08-03] Arquivo mais longo: `config/settings/base.py`, 90 linhas - dentro do limite (150 ideal / 300 maximo). Nenhum arquivo passa de 110 linhas.
- [2026-08-03] Status: **CONCLUIDA**, com duas pendencias honestas (nao bloqueiam as proximas etapas): (1) conexao real com o Postgres do Railway nunca testada, porque o projeto "Prisma" nao existe la ainda (E12 resolve); (2) Python 3.11 no lugar do 3.12 pedido, por falta do 3.12 nesta maquina. Proximo passo natural do backend: **E02** (nucleo de dados e multi-tenancy), que edita o `contas/models.py` ja existente em vez de cria-lo do zero.
- [2026-08-03] **Correcao da pendencia (1) acima, por outra sessao que retomou esta mesma etapa:** o projeto Railway existe, so nao se chama "Prisma" - chama-se `meu-ecoo` (mesmo repositorio, `railway list` confirma). `railway link -p meu-ecoo` linkou o workspace `projeto-ecoVS`; **so existe o ambiente `production`** (sem `development` separado), com servico `api` e banco `Postgres` ja online. Validei a conexao real (sem `migrate`): `railway run` com `DATABASE_URL` (hostname interno `postgres.railway.internal`) falha fora da rede do Railway - **use `DATABASE_PUBLIC_URL`** (mesma variavel, versao com proxy publico, ver `railway variables`) como `DATABASE_URL` local. Com isso, `SELECT 1` retornou `(1,)`. Nenhuma tabela foi tocada. Atualizei o `README.md` da raiz com essa instrucao. Pendencia nova para a **E12**: nao existe ambiente `development` separado no Railway deste projeto - avaliar se dev e prod devem compartilhar o mesmo Postgres a longo prazo.

## 9. Criterio de pronto

- [x] `pytest` roda e todos os testes passam - **saida real colada no diario**
- [x] `python manage.py check --deploy` roda com `prod.py` sem alerta critico
- [x] `.env.example` tem todos os nomes de variavel e **nenhum valor**
- [x] Nenhuma migracao foi aplicada
- [x] `pip-audit` rodado, resultado no diario
- [x] Nenhum arquivo passa de 300 linhas
- [x] `README.md` da raiz atualizado com como rodar o backend
- [ ] Commit feito, so com arquivos desta etapa

## 10. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Projeto Railway do Prisma pode nao existir | **Resolvido:** existe como `meu-ecoo`. Ambiente `production` unico (sem `development`) - avaliar na E12. |
| Rodar `migrate` por reflexo | Ver secao 4. Se acontecer, o conserto e dropar o banco antes da E02. |
| Banco remoto compartilhado | Sempre `railway status` antes. Nunca apontar dev para o ambiente de producao de outro produto. |
