# Contrato: modelo de dados

> Visao das entidades e de como elas se ligam entre os apps. Cada etapa
> implementa a sua parte; este documento existe para que as partes encaixem.
>
> **Isto e o desenho, nao o codigo.** Nomes de campo podem ganhar detalhe na
> implementacao - o que nao pode mudar sem decisao e o **relacionamento** e a
> **regra** descritos aqui.

## 1. A regra que atravessa tudo: `instituicao`

Quase toda entidade pertence a uma instituicao. Isso e o coracao do
multi-tenancy por coluna decidido na [visao geral](../VISAO-GERAL.md).

**Toda tabela de dominio carrega `instituicao` (FK, obrigatorio, indexado)** -
mesmo quando ela poderia ser derivada por join. A duplicacao e proposital: ela
permite filtrar por instituicao **sem depender de join correto**, que e
exatamente o tipo de erro que causa vazamento entre clientes.

Excecoes (nao pertencem a instituicao nenhuma):

- `Instituicao` - e a raiz
- Tabelas de configuracao global (ex.: tabela de conversao custo -> credito)
- Usuario da equipe interna (superusuario), que nao e de escola alguma

## 2. Mapa das entidades por app

```text
contas/
  Instituicao ──1:N── Usuario ──┬── perfil: ALUNO | PROFESSOR | DIRETOR
                                └── dados de menor (ver LGPD)

academico/
  Turma ──N:M── Usuario (via Matricula)
  Disciplina ──1:N── Turma
  Nota      ── aluno, disciplina, turma, valor, origem (MANUAL | IA)
  Falta     ── aluno, turma, data

conteudo/
  Material ── autor, turma?, arquivo (E08), status
  Prova ──1:N── Questao
  Prova ── status: RASCUNHO | OFICIAL, origem: MANUAL | IA

creditos/
  Lancamento (append-only) ── instituicao, usuario?, turma?, quantidade, tipo, motivo, referencia
  (saldo NAO e coluna - e derivado da soma)

ia/
  ChamadaIA ── usuario, classe_tarefa, modelo, tokens, custo, creditos_debitados, status
  (referenciada pelo Lancamento de debito)

memoria/
  Conversa ──1:N── Mensagem      (log bruto)
  MemoriaConsolidada             (resumo datado, imutavel, compactavel)
```

## 3. Entidades centrais - o que cada uma garante

### `Instituicao` (contas)

A raiz do tenant. Uma escola ou universidade. Tem nome, documento, status de
contrato e o pool de creditos da assinatura.

Nunca e apagada de verdade - desativar em vez de excluir. Apagar uma instituicao
levaria junto notas, historico e memoria de milhares de pessoas.

### `Usuario` (contas)

**Model customizado** (`AbstractUser`), definido antes da primeira migracao -
ver o alerta na [E01](../etapas/E01-fundacao-do-projeto.md).

Carrega:

- `instituicao` (FK) - a escola a que pertence. Nulo apenas para equipe interna.
- `perfil` - `ALUNO`, `PROFESSOR` ou `DIRETOR`. Um usuario tem **um** perfil.
- campos de LGPD para menor de idade - ver [contrato de LGPD](LGPD-E-DADOS-SENSIVEIS.md).

Login por e-mail, nao por `username`.

### `Lancamento` (creditos)

**Append-only.** Nunca sofre `UPDATE` nem `DELETE`. Estornar e criar um
lancamento contrario, nao apagar o original.

O saldo e sempre **derivado** da soma dos lancamentos - nunca uma coluna
`saldo` que alguem atualiza. Coluna de saldo diverge do historico no primeiro
bug de concorrencia; a soma nao mente.

### `ChamadaIA` (ia)

Registro de uma chamada ao motor de IA: quem pediu, que classe de tarefa, que
modelo respondeu, quantos tokens, quanto custou, quantos creditos foram
debitados, se deu certo.

E a **referencia de idempotencia** do debito: um retry da mesma chamada nao pode
debitar duas vezes.

### `Conversa` / `MemoriaConsolidada` (memoria)

A conversa bruta e persistida. A memoria consolidada e um resumo datado e
imutavel, que pode ser compactado com o tempo. Sao coisas diferentes e vivem
separadas de proposito - ver [E07](../etapas/E07-memoria-e-conversas.md).

## 4. Convencoes obrigatorias de model

| Convencao | Regra |
|-----------|-------|
| Nome de model | Singular, PascalCase, em portugues: `Turma`, `Lancamento` |
| Nome de campo | snake_case em portugues: `criado_em`, `data_nascimento` |
| Timestamps | Todo model tem `criado_em` e `atualizado_em` |
| Chave primaria | `BigAutoField` (padrao do projeto), **exceto** onde o id vaza para URL publica - ali use `UUIDField` |
| Exclusao | Preferir desativacao (`ativo=False`) a `DELETE` em entidade com historico |
| Dinheiro/credito | `DecimalField`, **nunca** `FloatField` |
| Escolhas | `models.TextChoices`, nunca string solta |
| Indice | `instituicao` sempre indexado; todo campo usado em filtro frequente tambem |

## 5. Migracoes

- Toda mudanca estrutural e versionada. Nunca ajuste manual no banco.
- **O banco e compartilhado e remoto (Railway).** Rodar `migrate` afeta todo
  mundo que estiver usando aquele ambiente. Combine antes.
- Migracao que apaga ou renomeia coluna com dado real exige registro no
  [`IA.md`](../../../IA.md) com o motivo.

## 6. Integridade que o banco deve garantir (nao so o Python)

Regra que so existe no codigo e regra que um dia sera violada por um script,
um shell ou uma migracao. Use o banco:

- `unique_together` / `UniqueConstraint` para matricula duplicada, e-mail por
  instituicao, etc.
- `CheckConstraint` para valor de nota dentro da faixa valida.
- `on_delete` **explicito e pensado** em toda FK. `CASCADE` numa FK de
  `Instituicao` significa "apagar a escola apaga tudo" - raramente e o que se
  quer. Prefira `PROTECT` onde a perda seria grave.
