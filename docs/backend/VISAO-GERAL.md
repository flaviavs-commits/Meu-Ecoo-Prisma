# Visao geral do backend

> Arquitetura e decisoes **ja travadas** do backend do Prisma. Este documento
> nao e uma etapa de trabalho: e o chao comum sobre o qual as 13 etapas rodam.
>
> Origem das decisoes: questionario de alinhamento respondido em 2026-08-01,
> mais as decisoes herdadas registradas no [`IA.md`](../../IA.md).

## 1. O que o sistema e

Plataforma SaaS de estudos vendida **a instituicoes de ensino** - escolas e
universidades. A instituicao assina, recebe creditos de IA, e o diretor
distribui esses creditos entre professores e alunos.

Tres perfis, com objetivos diferentes:

| Perfil | Faz o que | Precisa do backend |
|--------|-----------|--------------------|
| Aluno | Estuda | Tutor de IA com memoria, materiais gerados, simulados, notas e faltas |
| Professor | Ensina | Gera e corrige provas, material didatico, lanca notas, ve a turma |
| Diretor | Administra | Dashboards, gestao de usuarios e turmas, distribuicao de creditos |

**Nao ha autocadastro.** A conta da instituicao e criada pela equipe interna
apos o contrato ser fechado; alunos e professores sao cadastrados pela
instituicao. Qualquer tela ou fluxo que ofereca "criar minha conta" e residuo de
um modelo antigo e deve ser tratado como bug.

> **Residuo conhecido:** `frontend/src/content/landing.ts` ainda anuncia tres
> planos individuais pagos (Prisma / Pro / Ultra). Isso e da era em que o
> produto era vendido direto ao aluno. **O backend nao deve modelar plano
> individual.** A limpeza da landing e trabalho do frontend.

## 2. Stack

| Camada | Escolha | Observacao |
|--------|---------|------------|
| Linguagem | Python 3.12 | Versao da maquina de desenvolvimento |
| Framework | Django + Django REST Framework | Monolito modular |
| Banco | PostgreSQL **hospedado no Railway** | Mesmo provedor em dev e producao. Sem Postgres local, sem container de banco. |
| Dependencias | `pip` + `requirements.txt` com versoes fixadas | Lockfile commitado, `pip-audit` ao adicionar dependencia |
| Autenticacao | JWT (`djangorestframework-simplejwt`) | Frontend e uma SPA React separada |
| IA | OpenRouter, atras de um gateway proprio | Frontend nunca fala com o OpenRouter |
| Testes | `pytest` + `pytest-django`, TDD | Teste antes do codigo |
| Deploy | Railway | |

## 3. Estrutura

Apps Django **por dominio** - convencao nativa do framework. Foi escolhida em
vez da estrutura generica em camadas (`api/services/domain/repositories/`) do
guia Felixo, para nao criar duas hierarquias concorrentes no mesmo projeto.

```text
backend/
├── config/              # settings por ambiente, urls raiz, wsgi
├── contas/              # instituicao, usuario, perfis, autenticacao
├── academico/           # turmas, matriculas, notas, faltas
├── conteudo/            # materiais, provas, questoes, rascunho -> oficial
├── creditos/            # ledger, alocacao, saldo
├── ia/                  # gateway, provedores, contabilidade de uso
├── memoria/             # conversas do tutor e memoria consolidada
├── tests/               # testes que cruzam apps
├── manage.py
├── requirements.txt
└── .env.example
```

Dentro de cada app, a separacao de responsabilidade continua valendo: regra de
negocio em `services/`, acesso a dados em `models.py` e managers, HTTP em
`views.py` e `serializers.py`. **View fina**: recebe, valida, delega.

## 4. Decisoes travadas - nao reabrir sem decisao humana

Estas foram respondidas explicitamente. Uma etapa que discordar deve registrar a
objecao no diario e perguntar, nao decidir sozinha.

### 4.1 Multi-tenancy: coluna, nao schema

Todas as instituicoes convivem no mesmo banco e no mesmo schema. Cada registro
que pertence a uma instituicao carrega `instituicao_id`.

Foi escolhido em vez de schema-por-escola (`django-tenants`) e de banco-por-escola:
o ganho de isolamento nao paga a complexidade de migracao e operacao nesta
escala. Escala esperada de partida: **um cliente grande, cerca de 5 mil alunos**.

O risco conhecido dessa escolha e vazamento entre instituicoes por consulta sem
filtro. A mitigacao e estrutural e obrigatoria - ver
[E02](etapas/E02-nucleo-de-dados-e-multitenancy.md).

### 4.2 Creditos: termina a tarefa, depois bloqueia

Se o saldo zerar **durante** uma chamada de IA ja em andamento, a chamada
termina e e debitada normalmente, **mesmo que o saldo fique negativo**. O
bloqueio vale para a **proxima** chamada.

Nunca cortar uma resposta pela metade foi preferido a nunca deixar o saldo
negativar. Consequencia aceita: o saldo pode ficar negativo pelo custo de uma
unica chamada.

### 4.3 Conteudo de IA nasce rascunho

Prova, correcao ou nota gerada por IA entra no sistema como **rascunho**. So
vira oficial apos acao explicita do professor. E decisao pedagogica e de
responsabilidade, nao detalhe de UI: o backend precisa ter os dois estados e
exigir a transicao explicita.

### 4.4 Acoes destrutivas exigem confirmacao extra

Tres acoes nao podem ser um simples `DELETE` ou `PATCH`:

1. diretor zerar ou remover creditos de um perfil ou turma;
2. remover aluno ou professor da instituicao;
3. transformar prova ou nota gerada por IA em oficial.

O padrao de confirmacao e definido uma vez em
[E04](etapas/E04-autorizacao-e-perfis.md) e reusado pelas outras etapas.

### 4.5 Memoria do tutor: conversa bruta **e** memoria compactada

A conversa do aluno com o tutor **e** persistida em banco. Em paralelo, existe
uma memoria consolidada que e compactada com o tempo.

> Isto **refina** o registro de 2026-07-16 do `IA.md` ("memoria por resumos
> consolidados, nao conversa crua"). Hoje os dois coexistem: o log bruto da
> conversa e a memoria que evolui. Ver [E07](etapas/E07-memoria-e-conversas.md).

### 4.6 Escopo desta primeira entrega

**Entra:** fundacao Django, autenticacao dos 3 perfis, autorizacao, ledger de
creditos, upload de material, estrutura do gateway de IA, dominio academico e de
conteudo, admin de onboarding, deploy.

**Fica de fora, por decisao explicita:**

| Fora de escopo | Por que |
|---------------|---------|
| Chamada real ao OpenRouter | So a estrutura que vai receber isso. Sem chave configurada, sem chamada de verdade. |
| Pagamento / assinatura real | Cobranca da escola segue fora do sistema por enquanto. |
| Painel administrativo proprio | Django Admin resolve esta fase. Painel proprio e etapa futura. |
| Armazenamento em nuvem (S3) | Arquivo vai para disco. Migra se e quando a API escalar horizontalmente. |

## 5. Principios que valem em todas as etapas

1. **Simplicidade verificavel.** Sem fila, cache, microservico ou abstracao sem
   necessidade demonstrada.
2. **Integracao externa isolada.** O sistema nunca depende do formato cru de um
   provedor externo. Sempre atras de um adaptador proprio.
3. **Extensao antes de modificacao.** Comportamento que varia de forma previsivel
   (classe de tarefa de IA, tipo de material, regra de credito) e ponto de
   extensao, nao cadeia de `if`.
4. **Contrato estavel.** Formato de resposta e de erro definido uma vez, em
   [`contratos/API-CONVENCOES.md`](contratos/API-CONVENCOES.md), e mantido.
5. **Dado pessoal e cidadao de primeira classe.** Ha menores de idade na base.
   Ver [`contratos/LGPD-E-DADOS-SENSIVEIS.md`](contratos/LGPD-E-DADOS-SENSIVEIS.md).

## 6. Contratos compartilhados

Documentos que **todas** as etapas respeitam. Leia o que a sua etapa tocar:

| Contrato | Quando abrir |
|----------|--------------|
| [`API-CONVENCOES.md`](contratos/API-CONVENCOES.md) | Ao criar qualquer endpoint |
| [`MODELO-DE-DADOS.md`](contratos/MODELO-DE-DADOS.md) | Ao criar ou alterar model |
| [`LGPD-E-DADOS-SENSIVEIS.md`](contratos/LGPD-E-DADOS-SENSIVEIS.md) | Ao tocar em dado de pessoa |
| [`GLOSSARIO.md`](contratos/GLOSSARIO.md) | Ao nomear qualquer coisa |

## 7. Coordenação do canvas

- [2026-08-03] **/Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/VISAO-GERAL.md** iniciou a retomada do MVP e auditou o painel de etapas, o protocolo do agente e a árvore de trabalho. Estado desta retomada: **BLOQUEADO para nova implementação**; E02 está atribuída a `agente-canvas-E02` e marcada `BLOQUEADA`, enquanto E05, E08, E12 e E13 têm trabalho paralelo registrado. A auditoria confirmou que o projeto Railway correto agora existe como `Meu-Ecoo-Prisma`, com Postgres e serviço `api` online; porém os testes locais ainda apontam para um Postgres local inexistente (`role "prisma" does not exist`). Não apliquei migrações porque a E02 pertence a outro agente e a operação altera estado compartilhado. Próximo passo concreto: o responsável da E02 deve configurar a conexão pública do Railway, revisar/aplicar a migração e registrar a validação, ou o painel deve atribuir uma etapa livre. Validação: `manage.py check` passou; `pytest backend/tests backend/contas -q` resultou em `3 passed, 2 errors` por conexão local; `railway status` confirmou o projeto e os serviços online.
