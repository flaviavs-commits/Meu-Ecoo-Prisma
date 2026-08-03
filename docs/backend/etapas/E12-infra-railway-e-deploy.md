# E12 - Infra Railway e deploy

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
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

_(vazio - primeira entrada e sua)_

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
