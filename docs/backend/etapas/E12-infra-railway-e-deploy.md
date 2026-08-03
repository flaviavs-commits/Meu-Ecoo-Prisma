# E12 - Infra Railway e deploy

> **Status:** AGUARDANDO DECISAO · **Responsavel:** Claude (agente de infra)
> **Depende de:** E01 · **Destrava:** -
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Colocar o backend no ar no Railway, com banco, variaveis, volume de arquivos e
health check funcionando - e deixar o caminho de deploy documentado para quem
vier depois.

Depende so de E01, entao pode correr em paralelo com E02-E11.

## 2. Pre-requisitos

- E01 `CONCLUIDA`
- `railway` CLI autenticado - ver [`../FERRAMENTAS-E-ECOSSISTEMA.md`](../FERRAMENTAS-E-ECOSSISTEMA.md)
- **Coordenar com quem estiver na E08** - o volume de arquivos e requisito dela

## 3. ⚠️ Antes de qualquer comando

A conta Railway `projeto-ecoVS` hospeda **varios produtos da empresa em
producao**. Um comando no projeto errado atinge o sistema de outra equipe.

```bash
railway whoami
railway list
railway status     # SEMPRE antes de qualquer acao
```

Confirme projeto **e** ambiente antes de `run`, `up`, `variables` ou qualquer
coisa que escreva. Registre no diario qual projeto voce linkou.

Se o projeto do Prisma nao existir, **pergunte antes de criar** - projeto novo
tem custo. Marque a etapa como `AGUARDANDO DECISAO`.

## 4. Escopo

**Entra:** projeto e ambientes no Railway, Postgres, variaveis, volume, build e
start, health check, logs, migracao em producao, integracao com o HUD.

**Nao entra:** CI/CD completo com testes automaticos em PR (registre como
melhoria) e dominio proprio com HTTPS customizado, se ainda nao houver dominio
definido.

## 5. Como fazer

### 5.1 Ambientes

No minimo dois: `production` e um de trabalho (`development` ou `staging`).

**Um banco por ambiente.** Se desenvolvimento e producao compartilharem o mesmo
Postgres, uma migracao de teste derruba o cliente. Como a decisao foi usar
Postgres do Railway tambem em dev, essa separacao **e** o que protege producao.

Confirme e registre no diario qual banco cada ambiente usa.

### 5.2 Variaveis

Do `.env.example` de E01. Configure por ambiente:

```bash
railway variables --set DJANGO_SETTINGS_MODULE=config.settings.prod
```

- `DJANGO_SECRET_KEY` **diferente** por ambiente, gerada aleatoriamente;
- `DJANGO_DEBUG=False` em producao, sem excecao;
- `DATABASE_URL` vem do proprio Railway;
- `CORS_ALLOWED_ORIGINS` com a origem real da SPA - nunca `*` em producao.

**Nunca** cole valor de variavel no diario, em commit ou em documento.

### 5.3 Build e start

O Railway detecta Django via Nixpacks. Defina explicitamente mesmo assim - o que
e implicito quebra em silencio.

- servidor WSGI de producao (`gunicorn`), nunca `runserver`;
- `whitenoise` para estatico do admin;
- `collectstatic` no build;
- **`migrate` nao roda automaticamente no start.** Um deploy com migracao
  quebrada derrubaria a aplicacao em loop. Rode migracao como passo deliberado:
  `railway run python manage.py migrate`.

Registre a decisao sobre migracao automatica - e o tipo de coisa que o proximo
agente muda "para facilitar" sem saber por que estava assim.

### 5.4 Volume para arquivos

E08 guarda arquivo em disco. **Sem volume montado, todo arquivo enviado some no
proximo deploy.**

- crie um volume no servico e monte no caminho de midia;
- a variavel de caminho de midia aponta para o ponto de montagem;
- **teste de verdade**: suba um arquivo, faca um redeploy, baixe o arquivo de
  novo. Se nao fez esse teste, nao esta validado.

Volume nao e compartilhado entre replicas. Enquanto houver uma instancia,
funciona. Registre isso como limite conhecido - e o que dispara a migracao para
armazenamento em nuvem no futuro.

### 5.5 Health check e observabilidade

- aponte o health check do Railway para `/api/v1/health/` (E01);
- confirme que a rota **nao** exige autenticacao;
- `railway logs` para acompanhar;
- log em formato consistente, **sem dado pessoal** (contrato de LGPD).

Um health check que so responde "ok" sem tocar o banco esconde o problema mais
comum (banco fora). Considere verificar a conexao - e registre o que escolheu.

### 5.6 Seguranca de producao

Rode e resolva:

```bash
railway run python manage.py check --deploy
```

Confira: `DEBUG=False`, `ALLOWED_HOSTS` explicito, `SECURE_SSL_REDIRECT`,
`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS, admin em caminho proprio
(E11).

### 5.7 Integracao com o HUD

O padrao de qualidade exige `start_app.py` na raiz como porta de entrada unica.
Ele ja existe: e um HUD grafico (Tkinter) em `scripts/hud/`, hoje voltado ao
frontend.

O backend precisa aparecer ali - rodar a API, rodar testes, aplicar migracao.

> **`scripts/hud/` e area compartilhada com o frontend.** Nao reescreva o HUD.
> Adicione acoes no modulo proprio (`scripts/hud/acoes.py`), em commit separado,
> e avise no diario. Editar arquivo de outra frente sem aviso e o tipo de coisa
> que ja causou perda de trabalho neste repositorio (registro de 2026-07-31 no
> `IA.md`).

Se preferir nao tocar no HUD agora, entregue os comandos documentados no
`README.md` e registre a pendencia.

### 5.8 Verificacao - com evidencia real

Nada aqui e validado por leitura de configuracao:

1. deploy sobe e o servico fica saudavel;
2. `GET /api/v1/health/` responde 200 **na URL publica**;
3. migracao aplica e `showmigrations` confirma;
4. arquivo sobrevive a um redeploy (teste do 5.4);
5. `check --deploy` sem alerta critico;
6. `DEBUG` e realmente `False` em producao - verificado pela resposta de um erro;
7. CORS aceita a origem da SPA e recusa outra.

Cole a saida real de cada um no diario.

## 6. Contrato de saida

- backend no ar no Railway, com URL publica
- ambientes separados, com bancos separados
- variaveis configuradas, sem segredo no repositorio
- volume montado e comprovado
- health check ativo
- caminho de deploy documentado no `README.md`

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Comando no projeto errado | `railway status` antes de tudo. Registrar o projeto linkado. |
| Dev e producao no mesmo banco | Ambientes separados. Confirmar, nao presumir. |
| Arquivo sumindo no deploy | Volume + teste de redeploy real |
| `migrate` automatico quebrando o servico | Migracao como passo deliberado |
| Editar o HUD e atropelar o frontend | Commit separado + aviso |
| Segredo em log ou documento | Nunca colar valor de variavel |
| Volume nao escala com replicas | Limite conhecido, registrado |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Peguei a etapa e conferi as dependencias antes de mexer em qualquer coisa no Railway - `E01` esta `EM ANDAMENTO` (outro agente), ainda **nao concluida**, e a pasta `backend/` nao existe neste repositorio. Sem projeto Django, nao ha o que fazer build/deploy/migrate/health-check ainda.
- [2026-08-03] Rodei o preflight de infra, sem nenhuma acao destrutiva:
  ```
  railway whoami --json   -> conta projeto-ecoVS (flaviavs@vitissouls.com), workspace "projeto-ecoVS's Projects"
  railway list            -> 13 projetos no workspace, entre eles: Vitis Souls - Servidor Geral, meu-ecoo, minha-motivacao-e-proposito,
                             social-api-back-end-db, descvip-ad-studio, Contas.exe, descvip-bot-prom, Financeiro,
                             Area-Saude-Mental, discord-center, prj-app-conselheiro-vip, taskforge-internal-production,
                             intelligent-vitality
  railway status          -> projeto linkado localmente por padrao: "meu-ecoo" (env production), servico "api" Online
                             (https://api-production-1b34.up.railway.app) + Postgres "postgres-volume" Online
  ```
- [2026-08-03] Investiguei o servico `api` do projeto `meu-ecoo` antes de presumir que era o alvo certo (regra anti-alucinacao). As variaveis configuradas la sao `NODE_ENV`, `JWT_SECRET`, `JWT_EXPIRES_IN`, `EMAIL_HOST*`, `PARTNER_*`, `ADMIN_INBOUND_SERVICE_TOKEN` - perfil de app **Node.js**, nao Django. Nao ha `DJANGO_SECRET_KEY`, `DJANGO_SETTINGS_MODULE` nem nada compativel com o `.env.example` que E01 vai gerar. **Nao e o projeto do Prisma** apesar do nome parecido ("meu-ecoo") - e outro produto da empresa, ja em producao. Nenhum valor de variavel foi exposto (usei `railway variables --kv` e mascarei tudo antes de registrar aqui).
  - Nao encontrei, em `railway list`, nenhum projeto com nome obvio para "Prisma"/"ecoo-prisma"/"backend-prisma".
- [2026-08-03] Conclusao: nao ha nem projeto Railway do Prisma nem codigo Django para deployar. Duas coisas bloqueiam esta etapa ao mesmo tempo:
  1. `E01` precisa concluir (gera `backend/`, `.env.example`, `requirements.txt`) antes de haver o que buildar.
  2. Falta decisao humana sobre criar um projeto Railway novo para o Prisma (custo, conforme a secao 3 desta etapa manda perguntar antes de criar).
  Marquei o status como `AGUARDANDO DECISAO` em vez de `BLOQUEADA` porque o bloqueio de E01 e temporario (ela esta em andamento), mas a criacao de projeto novo exige resposta humana antes que eu prossiga - nao vou criar projeto Railway sem confirmacao.
- [2026-08-03] Nao linkei nada, nao criei nada, nao rodei `railway variables --set` nem qualquer comando de escrita. O link local em `meu-ecoo`/`production` que o CLI mostrou ja existia antes desta sessao (nao fui eu quem linkou) - registrando para quem ler depois nao presumir que essa e a infra do Prisma.
- [2026-08-03] Proximo passo assim que houver resposta: se a decisao for criar projeto novo, rodar `railway init` com nome explicito (ex.: `meu-ecoo-prisma-backend` ou equivalente definido com o time) e criar os dois ambientes (`production` + `development`) com bancos Postgres separados (secao 5.1), so entao passar para variaveis/build quando `backend/` existir (E01 concluida).
- [2026-08-03] Revisao apos a separacao dos projetos Meu Ecoo e Meu Ecoo Prisma - a conta Railway informa assinatura vencida; nao executei deploy, migracao, alteracao de variavel ou outro comando de escrita. O MVP segue validado localmente com SQLite, e esta etapa permanece AGUARDANDO DECISAO ate a regularizacao da cobranca e autorizacao de infraestrutura.

## 9. Criterio de pronto

- [ ] As 7 verificacoes do item 5.8 feitas, com saida real no diario
- [ ] Projeto e ambiente Railway registrados no diario
- [ ] Nenhum valor de variavel aparece em arquivo, commit ou diario
- [ ] Volume comprovado com redeploy de verdade
- [ ] `check --deploy` limpo
- [ ] Decisao sobre migracao automatica registrada
- [ ] HUD atualizado **ou** pendencia registrada, com aviso ao frontend
- [ ] `README.md` documenta o deploy
- [ ] `IA.md` atualizado com a topologia de infra
- [ ] Commit feito, so com arquivos desta etapa
