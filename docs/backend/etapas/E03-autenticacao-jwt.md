# E03 - Autenticacao JWT

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
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

_(vazio - primeira entrada e sua)_

## 9. Criterio de pronto

- [ ] Os 8 testes do item 5.8 passam - saida real no diario
- [ ] Argon2 configurado como hasher principal
- [ ] Rate limit ativo, numero escolhido registrado
- [ ] Nenhuma resposta revela se o e-mail existe
- [ ] Payload do token sem dado pessoal - verificado decodificando um token real
- [ ] Decisao sobre unicidade de e-mail registrada
- [ ] Decisao (ou pendencia) sobre armazenamento do token registrada
- [ ] `IA.md` atualizado com a decisao de autenticacao
- [ ] Commit feito, so com arquivos desta etapa
