# E01 - Fundacao do projeto

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
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

_(vazio - primeira entrada e sua)_

## 9. Criterio de pronto

- [ ] `pytest` roda e todos os testes passam - **saida real colada no diario**
- [ ] `python manage.py check --deploy` roda com `prod.py` sem alerta critico
- [ ] `.env.example` tem todos os nomes de variavel e **nenhum valor**
- [ ] Nenhuma migracao foi aplicada
- [ ] `pip-audit` rodado, resultado no diario
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] `README.md` da raiz atualizado com como rodar o backend
- [ ] Commit feito, so com arquivos desta etapa

## 10. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Projeto Railway do Prisma pode nao existir | Confirmar com `railway list`. Se faltar, e bloqueio da E12 - registrar, nao criar por conta propria. |
| Rodar `migrate` por reflexo | Ver secao 4. Se acontecer, o conserto e dropar o banco antes da E02. |
| Banco remoto compartilhado | Sempre `railway status` antes. Nunca apontar dev para o ambiente de producao de outro produto. |
