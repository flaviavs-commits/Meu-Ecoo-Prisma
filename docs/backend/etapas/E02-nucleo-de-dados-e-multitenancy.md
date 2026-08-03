# E02 - Nucleo de dados e multi-tenancy

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
> **Depende de:** E01 · **Destrava:** E03 a E11
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Criar as duas entidades que sustentam o sistema inteiro - `Instituicao` e
`Usuario` - e o mecanismo que **impede uma escola de enxergar dado de outra**.

Esta e a etapa mais perigosa do projeto. Um erro aqui nao aparece como bug:
aparece como vazamento de dado entre clientes.

## 2. Pre-requisitos

- E01 `CONCLUIDA` (projeto Django rodando, **sem migracao aplicada**)
- Ter lido [`../contratos/MODELO-DE-DADOS.md`](../contratos/MODELO-DE-DADOS.md)
- Ter lido [`../contratos/LGPD-E-DADOS-SENSIVEIS.md`](../contratos/LGPD-E-DADOS-SENSIVEIS.md)

## 3. Escopo

**Entra:**

- model `Instituicao`
- model `Usuario` customizado (`AUTH_USER_MODEL`), com perfil e campos de LGPD
- base abstrata + manager que aplicam o escopo de instituicao
- a **primeira migracao** do projeto
- testes que provam que o isolamento funciona

**Nao entra:**

- login e token (E03)
- regras de quem pode o que (E04)
- qualquer model de outro dominio

## 4. Decisoes ja travadas - nao reabrir

| Decisao | Valor |
|---------|-------|
| Multi-tenancy | **Coluna `instituicao_id`** em cada tabela. Nao schema, nao banco separado. |
| Perfil | Um usuario tem **um** perfil: `ALUNO`, `PROFESSOR` ou `DIRETOR` |
| Login | Por **e-mail**, nao por `username` |
| Menores | Ha menores na base. Campos de consentimento sao obrigatorios no model. |

## 5. Como fazer

### 5.1 `Instituicao`

Campos minimos: `nome`, `documento` (CNPJ), `ativa`, `criado_em`,
`atualizado_em`.

Nunca e apagada - desativar em vez de excluir. Apagar uma instituicao levaria
junto o historico academico de milhares de pessoas.

### 5.2 `Usuario`

Herda de `AbstractUser` (nao `AbstractBaseUser` - o ganho nao paga o trabalho).

| Campo | Regra |
|-------|-------|
| `email` | Unico **por instituicao**, nao globalmente. Usado no login. |
| `instituicao` | FK. Nulo **apenas** para equipe interna (superusuario). |
| `perfil` | `TextChoices`: `ALUNO`, `PROFESSOR`, `DIRETOR` |
| `data_nascimento` | Obrigatorio para aluno - e o que define se e menor |
| `responsavel_nome` | Preenchido quando menor |
| `responsavel_contato` | Preenchido quando menor |
| `consentimento_responsavel_em` | Nulo = pendente. Estado visivel, nao esquecido. |
| `ativo` | Desativar em vez de apagar |

Adicione uma propriedade `e_menor` derivada de `data_nascimento` - a idade muda
sozinha com o tempo, entao **nunca** guarde "e menor" como coluna booleana.

Remova `username` do fluxo (`USERNAME_FIELD = "email"`), mas atencao: `email`
unico por instituicao significa que `USERNAME_FIELD` sozinho nao garante
unicidade global. Documente como o login resolve isso - ver E03, secao de
riscos.

### 5.3 O mecanismo de isolamento - o coracao da etapa

Tres camadas, porque uma so sempre falha em algum ponto:

**Camada 1 - base abstrata.** Um `ModeloDaInstituicao(models.Model)` abstrato
com `instituicao` FK obrigatoria e indexada. Todo model de dominio herda dele.

**Camada 2 - manager que obriga o escopo.** Um queryset com
`da_instituicao(instituicao)`. O manager padrao **nao** deve silenciosamente
retornar tudo em contexto de request.

> **Nao use thread-local nem middleware magico para injetar o tenant.** Parece
> conveniente e falha em tarefa assincrona, comando de management e teste - e
> falha silenciosamente, que e o pior tipo. O escopo e **explicito**.

**Camada 3 - teste que varre o projeto.** Um teste que percorre todos os models
concretos e falha se algum model de dominio nao herdar da base. E o unico jeito
de garantir que o proximo agente, daqui a tres etapas, nao esqueca.

### 5.4 Recurso de outra instituicao responde 404

Nao 403. Responder 403 confirma que aquele id existe - e vazamento de
informacao entre clientes concorrentes. Isso vira mixin de view em E04, mas a
**regra** nasce aqui e o teste tambem.

### 5.5 A primeira migracao

Agora sim:

```bash
railway status                    # confirme o ambiente ANTES
railway run python manage.py makemigrations contas
railway run python manage.py migrate
```

Confira o SQL antes de aplicar (`sqlmigrate`) e cole no diario o resultado real.

### 5.6 TDD - ordem sugerida

1. Teste: criar instituicao e usuario com perfil. Falha (nao existe).
2. Implementa os models.
3. Teste: usuario da instituicao A **nao** consegue enxergar registro da
   instituicao B via manager. Falha.
4. Implementa a base + manager.
5. Teste: todo model de dominio herda da base. Falha ou passa vazio - deixe
   pronto para as proximas etapas.
6. Teste: `e_menor` responde certo para data de nascimento limite (aniversario
   hoje, 17 anos e 364 dias, 18 anos exatos).

## 6. Contrato de saida

- `contas.Instituicao` e `contas.Usuario` existem e estao migrados
- `AUTH_USER_MODEL` funcionando - `get_user_model()` retorna `Usuario`
- base abstrata `ModeloDaInstituicao` disponivel para os outros apps
- manager com `da_instituicao(...)` disponivel
- teste estrutural que falha se um model novo esquecer o escopo
- regra "404, nao 403" documentada e testada

**Todo model criado depois desta etapa herda da base.** Nao ha excecao sem
registro no `IA.md`.

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Consulta sem filtro vaza dado entre escolas | As 3 camadas do item 5.3. O teste estrutural e o que sobrevive ao tempo. |
| `AUTH_USER_MODEL` trocado depois de migrar | Se E01 respeitou o alerta, esta e a primeira migracao. Confirme com `showmigrations` antes. |
| `email` unico por instituicao complica o login | Decisao de E03. Registre aqui o que voce escolheu no model para nao contradizer. |
| Alguem tratar `e_menor` como coluna | Propriedade derivada. Se virar coluna, fica errada no aniversario. |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Uma entrada por decisao, bug, bloqueio ou teste rodado.
> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

_(vazio - primeira entrada e sua)_

## 9. Criterio de pronto

- [ ] Migracao aplicada no Railway - saida real no diario
- [ ] Teste de isolamento entre instituicoes passa
- [ ] Teste estrutural (todo model herda da base) existe e passa
- [ ] Teste de `e_menor` cobre os casos de borda
- [ ] Campos de LGPD presentes, conforme o contrato
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] Decisao sobre unicidade de e-mail registrada no diario
- [ ] `IA.md` da raiz atualizado com a decisao de multi-tenancy aplicada
- [ ] Commit feito, so com arquivos desta etapa
