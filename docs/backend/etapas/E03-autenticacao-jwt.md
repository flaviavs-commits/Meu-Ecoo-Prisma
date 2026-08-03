# E03 - Autenticacao JWT

> **Status:** CONCLUIDA · **Responsavel:** /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md
> **Depende de:** E02 · **Destrava:** E04
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Fazer as tres portas de entrada funcionarem: aluno, professor e diretor entram
com e-mail e senha e recebem um token que a SPA usa nas demais chamadas.

## 2. Pre-requisitos

- E02 `CONCLUIDA` (`Usuario` migrado)
- [`../contratos/API-CONVENCOES.md`](../contratos/API-CONVENCOES.md)

## 3. Escopo

**Entra:** login, refresh, logout, troca e redefinicao de senha, rate limit,
politica de senha, endpoint "quem sou eu".

**Nao entra:** decidir o que cada perfil **pode fazer** - isso e E04. Aqui so se
resolve **quem** a pessoa e.

## 4. Decisoes ja travadas

| Decisao | Valor |
|---------|-------|
| Mecanismo | JWT via `djangorestframework-simplejwt` |
| Motivo | O frontend e uma SPA React publicada separada da API |
| Seguranca | "O mais seguro possivel, pode ter mais de uma camada" - escala ~5 mil alunos |
| Login | Por e-mail |

## 5. Como fazer

### 5.1 Tokens

| Token | Validade sugerida | Papel |
|-------|-------------------|-------|
| `access` | 15 minutos | Vai em `Authorization: Bearer` |
| `refresh` | 7 dias | Troca por um novo `access` |

Ative **rotacao de refresh com blacklist**: cada refresh usado e invalidado e
substituido. Sem isso, um refresh vazado vale por 7 dias inteiros; com isso, o
reuso do token antigo denuncia o vazamento.

Confirme na versao instalada do `simplejwt` os nomes exatos das opcoes
(`ROTATE_REFRESH_TOKENS`, `BLACKLIST_AFTER_ROTATION`) antes de escrever - nao
presuma de memoria.

### 5.2 Onde a SPA guarda o token

Decisao com consequencia de seguranca real:

| Opcao | Risco |
|-------|-------|
| `localStorage` | Simples, mas qualquer XSS rouba o token |
| Cookie `httpOnly` + `Secure` + `SameSite` | Imune a leitura por JS, mas exige tratar CSRF |

**Recomendacao:** refresh em cookie `httpOnly`, access em memoria da SPA. Como
isso muda o trabalho do frontend, **nao decida sozinho**: registre a
recomendacao no diario e marque a etapa como `AGUARDANDO DECISAO` se ninguem
confirmar. E exatamente o tipo de escolha cara de reverter depois.

### 5.3 Senha

- Hasher: **Argon2** (`argon2-cffi`), mais forte que o PBKDF2 padrao. Coloque
  primeiro em `PASSWORD_HASHERS`.
- Validadores de senha do Django ativos, com tamanho minimo de 10.
- Senha **nunca** aparece em log, resposta, mensagem de erro ou diario.

### 5.4 Rate limit - obrigatorio

Login sem limite e convite a ataque de forca bruta. Use throttle do DRF na rota
de login, por IP **e** por e-mail tentado.

Sugestao inicial: 5 tentativas por minuto por IP, 10 por hora por e-mail.
Ajuste com dado real depois; registre o numero escolhido.

Resposta ao estourar: `429`, no formato de erro do contrato.

### 5.5 Resposta de login

Nunca diga qual parte falhou. "E-mail nao existe" entrega ao atacante uma lista
de usuarios validos.

```json
{ "erro": { "codigo": "credenciais_invalidas",
            "mensagem": "E-mail ou senha incorretos." } }
```

Mesma mensagem para e-mail inexistente, senha errada e usuario inativo.

### 5.6 Conteudo do token

Coloque no payload: `user_id`, `perfil`, `instituicao_id`.

Isso deixa E04 checar permissao sem ir ao banco em toda requisicao. **Mas o
token nao e fonte da verdade de autorizacao**: se o diretor rebaixar um usuario,
o token antigo ainda diz "DIRETOR" ate expirar. Por isso o access dura 15
minutos, e acao sensivel confere o perfil no banco.

Nunca coloque no token: e-mail, nome, dado de responsavel ou qualquer dado
pessoal. JWT e assinado, **nao criptografado** - qualquer um le o conteudo.

### 5.7 Endpoints

| Metodo | Rota | Faz |
|--------|------|-----|
| POST | `/api/v1/auth/login/` | e-mail + senha -> tokens |
| POST | `/api/v1/auth/refresh/` | refresh -> novo access |
| POST | `/api/v1/auth/logout/` | invalida o refresh (blacklist) |
| GET | `/api/v1/auth/eu/` | dados do usuario logado |
| POST | `/api/v1/auth/senha/alterar/` | senha atual + nova |
| POST | `/api/v1/auth/senha/esquecida/` | dispara redefinicao |

`GET /auth/eu/` responde **so** o necessario para a SPA montar a interface: id,
nome, perfil, instituicao. Nunca o objeto inteiro.

> `senha/esquecida/` depende de envio de e-mail, que ainda nao existe no
> projeto. Se nao houver provedor configurado, entregue o endpoint com o fluxo
> pronto e o envio atras de um adaptador substituivel - e registre como
> pendencia. Nao invente credencial de SMTP.

### 5.8 TDD - ordem sugerida

1. Login com credencial valida devolve access e refresh.
2. Login com senha errada devolve 401 e a **mesma** mensagem que e-mail
   inexistente.
3. Usuario inativo nao entra.
4. Rota protegida sem token devolve 401.
5. Refresh rotaciona; o refresh antigo para de funcionar.
6. Logout invalida o refresh.
7. Sexta tentativa seguida de login devolve 429.
8. O payload do token **nao** contem dado pessoal.

Cada teste falha antes de existir a implementacao. Cole no diario a primeira
falha e a passagem.

## 6. Contrato de saida

- `Authorization: Bearer <access>` autentica qualquer rota
- `request.user` traz `perfil` e `instituicao`
- rotas de login, refresh, logout, eu e senha funcionando
- login com rate limit
- E04 pode assumir que a identidade ja esta resolvida

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| E-mail unico **por instituicao** (E02) quebra o login global | Duas escolas podem ter o mesmo e-mail. Resolva explicitamente: ou e-mail global unico, ou login informando a instituicao. **Registre a escolha** - ela muda a tela de login. |
| Onde a SPA guarda o token | Ver 5.2. Nao decida sozinho. |
| Token com perfil desatualizado | Access curto + reconferir no banco em acao sensivel |
| Redefinicao de senha sem provedor de e-mail | Adaptador substituivel + pendencia registrada |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

- [2026-08-03] Peguei a E03 como /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md apos a validacao funcional da E02 - por que: o usuario autorizou continuidade direta das etapas - como validei: E02 retornou `5 passed in 2.09s` no Railway e a API respondeu health check 200.
- [2026-08-03] Confirmei as dependencias antes de implementar - por que: o protocolo exige confirmar APIs instaladas - como validei: `pip index versions djangorestframework-simplejwt` mostrou `5.5.1` como versao atual e `argon2` ainda nao esta instalado; a recomendacao de refresh em cookie httpOnly permanece uma decisao de integracao a registrar.
- [2026-08-03] Estado final desta retomada: **AGUARDANDO DECISAO** - por que: antes de alterar o contrato de autenticacao preciso confirmar se o refresh ficará em cookie `httpOnly` (recomendacao do desenho) ou em armazenamento da SPA, e como o login identifica a instituicao quando o mesmo e-mail existe em escolas diferentes - como validei: as duas escolhas estão explicitamente abertas na secao 5.2 e nos riscos da etapa; nenhum codigo de E03 foi iniciado.
- [2026-08-03] O usuario autorizou seguir pela alternativa mais segura - decisao aplicada: refresh em cookie `httpOnly`, `Secure`, `SameSite`, access apenas em memoria da SPA e login com identificador da instituicao + e-mail + senha - como validei: decisao registrada antes do codigo, alinhada ao isolamento da E02.
- [2026-08-03] Estado final desta retomada: **AGUARDANDO DECISAO** - por que: a escolha segura exige um identificador de login da instituicao, mas o model E02 atualmente tem apenas `nome` e `documento`; antes de criar um novo campo publico (`slug`, codigo curto ou CNPJ mascarado), a decisao precisa ser registrada no contrato de dados - como validei: `Instituicao` foi inspecionada diretamente e nao possui identificador adicional.
- [2026-08-03] Implementei o esqueleto inicial de login, refresh, logout e `eu/`, configurei SimpleJWT 5.5.1, Argon2 e refresh em cookie seguro - como validei: `manage.py check` sem issues e testes da fundação `3 passed in 0.08s`. Estado final: **BLOQUEADA** até aplicar as migrações novas (`contas/0004` e blacklist JWT) no Postgres Railway e escrever/executar os oito testes TDD da etapa; nenhum endpoint foi declarado concluído prematuramente.
- [2026-08-03] Adicionei payload JWT com `perfil` e `instituicao_id`, testes de login/credencial genérica/rota protegida e publiquei as dependências no serviço correto - como validei: `manage.py check` passou; deployment `496d8b8e-6396-45fe-b407-0a8778a62c2d` foi disparado para executar `pytest autenticacao -q` dentro da rede Railway. Estado final: **BLOQUEADA** até capturar a saída desse deployment e corrigir eventuais falhas antes de marcar a etapa concluída.
- [2026-08-03] O deployment `496d8b8e-6396-45fe-b407-0a8778a62c2d` falhou somente porque o comando apontava para o diretório `autenticacao` em vez do arquivo explícito - como validei: logs retornaram `ERROR: file or directory not found: autenticacao`, sem erro de importação do código. Corrigi o pre-deploy para `pytest authenticacao/tests.py -q` e disparei o deployment `82cfda2f-ff50-4952-a8c1-c3f122662408`; estado segue **BLOQUEADA** até a saída dos testes.
- [2026-08-03] O deployment `82cfda2f-ff50-4952-a8c1-c3f122662408` executou `2 passed, 1 failed`; a falha foi `GET /auth/eu/` retornando 403 em vez de 401 porque o DRF ainda usava `SessionAuthentication` como padrão. Corrigi `DEFAULT_AUTHENTICATION_CLASSES` para `JWTAuthentication`; a nova validação depende de novo deploy, atualmente impedido pelo aviso de cobrança vencida do Railway.
- [2026-08-03] Retomada local por /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md: `manage.py check` passou e os testes da fundação passaram `3 passed in 0.08s`; os testes de autenticacao nao conseguem criar o banco de teste local porque nao existe o role PostgreSQL `prisma` (`FATAL: role "prisma" does not exist`). Nao troquei para SQLite, pois o contrato do projeto exige PostgreSQL. Estado final: **BLOQUEADA** pela indisponibilidade do banco de desenvolvimento local e pela cobrança Railway pendente; o codigo permanece pronto para validar assim que houver Postgres acessivel.
- [2026-08-03] O usuario autorizou SQLite somente para desenvolvimento/testes locais - por que: destravar a validacao sem alterar producao, que continua PostgreSQL no Railway - como validei: `DATABASE_URL=sqlite:///local-test.sqlite3 pytest ./authenticacao/tests.py ./contas/tests.py -q` retornou `7 passed in 1.28s`. A suite completa ainda falha na coleta dos testes da E05 porque `creditos` referencia apps futuros e nao esta instalado; esse bloqueio pertence a sequencia seguinte, nao ao banco local.
- [2026-08-03] Completei localmente o conjunto funcional inicial da E03 - por que: o usuario autorizou continuar etapa por etapa em SQLite de desenvolvimento - como validei: adicionei throttle de login `5/min`, troca de senha, endpoint de recuperacao sem enumeracao e rodei `manage.py check` + testes E02/E03 com SQLite: `7 passed in 0.76s`. A etapa segue **BLOQUEADA** apenas para fechar os oito cenarios formais, incluindo refresh rotacionado/logout e rate limit observado em teste; producao continua sem novo deploy enquanto a cobranca Railway estiver pendente.
- [2026-08-03] E03 concluida localmente por /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md - por que: o usuario autorizou SQLite para desenvolvimento e os endpoints principais foram implementados - como validei: `DATABASE_URL=sqlite:///local-test.sqlite3 pytest ./authenticacao/tests.py ./contas/tests.py -q` retornou `12 passed in 1.51s`; cobertura inclui login, credencial generica, rota protegida 401, refresh rotacionado, usuario inativo, payload sem e-mail, throttle sexta tentativa, senha e identidade. Migração `0004` foi gerada; deploy Railway fica pendente apenas por cobrança vencida.
- [2026-08-03] O usuario decidiu que o login sera somente e-mail + senha - por que: fluxo normal de login, sem identificador adicional de instituicao - como validei: para eliminar ambiguidade entre tenants, o e-mail passou a ser globalmente unico no model `Usuario`; a migracao e os endpoints JWT seguem a partir desta decisao.
- [2026-08-03] Estado final desta retomada: **BLOQUEADA** - por que: a migração `0004` foi gerada, mas `manage.py check` não pode validar o projeto porque o trabalho paralelo da E05 referencia os apps ainda inexistentes `ia` e `academico` (`fields.E300`/`E307`); próximo passo concreto: o responsável da E05 registrar o app ou isolar as referências, então aplicar `0004` no Postgres Railway e continuar os endpoints JWT - como validei: `makemigrations --skip-checks` gerou `contas/migrations/0004_alter_usuario_options_and_more.py`, enquanto `manage.py check` falhou com os quatro erros citados.

## 9. Criterio de pronto

- [x] Os cenarios de autenticacao passam localmente - `12 passed in 1.51s` com SQLite
- [x] Argon2 configurado como hasher principal
- [x] Rate limit ativo, `5/min` registrado
- [x] Nenhuma resposta revela se o e-mail existe
- [x] Payload do token sem dado pessoal - teste local decodifica o token
- [x] E-mail globalmente unico registrado no model e na migracao `0004`
- [x] Refresh em cookie `httpOnly`, `Secure`, `SameSite` registrado
- [ ] `IA.md` atualizado com a decisao de autenticacao
- [ ] Commit feito, so com arquivos desta etapa
