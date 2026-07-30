# Constituicao de Modularidade

> **Regra estrutural obrigatoria e permanente deste projeto.**
> Tem prioridade sobre preferencia pessoal de organizacao.
> Vale para qualquer IA que trabalhe aqui - Claude, ChatGPT, Codex, Gemini, Cursor.
>
> Resumo operacional e limites na secao 4 do [`AGENTS.md`](../AGENTS.md).
> Este documento e a versao completa, para consulta em refatoracao e revisao.

## Objetivo

Este projeto deve ser desenvolvido pensando primeiro na eficiencia de manutencao por IA e por humanos.

A prioridade **nao** e reduzir quantidade de arquivos.

A prioridade e reduzir:

- leitura desnecessaria;
- consumo de contexto;
- consumo de tokens;
- tempo de analise;
- risco de modificar codigo nao relacionado;
- conflitos durante repairs.

Toda alteracao futura deve permitir que uma IA consiga abrir **apenas os arquivos realmente envolvidos** naquela tarefa.

Nunca obrigue uma IA a ler centenas ou milhares de linhas para alterar apenas uma pequena funcionalidade.

## Principio fundamental

**Cada arquivo deve possuir UMA unica responsabilidade.**

Se um arquivo comeca a conter duas ou mais responsabilidades diferentes, ele deve ser dividido imediatamente.

A organizacao do projeto vale mais do que possuir poucos arquivos. E preferivel existir 40 arquivos de 80 linhas do que 1 arquivo de 3.000 linhas.

## Regra principal

Sempre que uma funcionalidade nova for criada, pergunte:

> "Essa responsabilidade ja pertence exatamente a este arquivo?"

Se a resposta nao for um "sim" absoluto, deve ser criado um novo modulo.

### Arquivos deposito sao proibidos

- `utils.ts`
- `helpers.ts`
- `misc.ts`
- `common.ts`
- `functions.ts`
- `services.ts` gigantes
- `components.tsx` contendo dezenas de componentes

Cada arquivo precisa possuir um proposito extremamente claro.

## Separacao obrigatoria

### Componentes

Cada componente em seu proprio arquivo. Nunca varios componentes grandes no mesmo arquivo.

```
/components
  Header.tsx
  Footer.tsx
  Hero.tsx
  Button.tsx
  Card.tsx
  Modal.tsx
  Loading.tsx
  Sidebar.tsx
```

### Hooks

Nunca varios hooks em um unico arquivo.

```
/hooks
  useAuth.ts
  useTheme.ts
  useAnimation.ts
  useUser.ts
```

### Contextos

Cada contexto em seu proprio arquivo.

```
/context
  ThemeContext.tsx
  UserContext.tsx
  AuthContext.tsx
```

### Funcoes

Nunca criar arquivos com dezenas de funcoes sem relacao. Cada funcao importante tem seu proprio arquivo quando fizer sentido.

```
formatCurrency.ts
formatDate.ts
calculateDiscount.ts
generateSlug.ts
maskCPF.ts
```

### Tipos

Nunca concentrar todos os tipos em um unico arquivo enorme.

```
/types
  User.ts
  Product.ts
  Coupon.ts
  Order.ts
```

### Constantes

```
/constants
  colors.ts
  routes.ts
  limits.ts
  storage.ts
  api.ts
```

### Conteudo

Cada bloco textual separado.

```
/content
  landing.ts
  faq.ts
  benefits.ts
  pricing.ts
```

### CSS

Nunca criar um `index.css` gigantesco. Separar quando necessario:

```
variables.css
fonts.css
layout.css
animations.css
buttons.css
cards.css
```

### Python

Nunca criar arquivos Python enormes. Separar por responsabilidade:

```
app.py
routes.py
database.py
config.py
scheduler.py
logger.py
hud.py
window.py
terminal.py
actions.py
automation.py
```

## Criterio de quebra

Nao dividir apenas por quantidade de linhas. **Dividir por responsabilidade.**

Um arquivo deve conseguir ser descrito em uma frase simples:

- "Esse arquivo desenha o Header."
- "Esse arquivo controla a autenticacao."
- "Esse arquivo renderiza os cartoes."

Se forem necessarias palavras como **e**, **alem disso**, **tambem**, **outra coisa** - entao provavelmente existem responsabilidades demais.

## Limites recomendados

Servem como **alerta estrutural**, nao como proibicao automatica.

| Tipo | Ideal | Alerta | Maximo |
|------|-------|--------|--------|
| Componente React | 120 | 150 | 200 |
| Hook | 80 | - | 150 |
| Modulo Python | 150 | 200 | 300 |
| Arquivo de conteudo | 150 | - | 250 |
| Arquivo CSS | 150 | - | 250 |
| Documento | 250 | - | 400 |

## Reparos

Durante qualquer repair, a IA deve abrir **apenas os arquivos necessarios**.

E proibido:

- reler o projeto inteiro;
- modificar arquivos sem necessidade;
- centralizar codigo;
- mover responsabilidades para arquivos maiores.

Se uma alteracao exige apenas um componente, somente aquele componente deve ser alterado.

## Refatoracoes

Sempre que identificar um arquivo crescendo excessivamente:

- extrair componentes;
- extrair funcoes;
- extrair hooks;
- extrair constantes;
- extrair tipos;
- extrair utilidades especificas.

**Nunca esperar o arquivo ficar gigantesco para modularizar.**

## Economia de tokens

Esta regra existe principalmente para reduzir consumo de tokens, custo computacional, tempo de leitura, tempo de repair e contexto desperdicado.

Arquivos pequenos tornam as respostas da IA mais rapidas, mais precisas, e reduzem drasticamente a chance de efeitos colaterais.

## Criterio de pronto

Uma tarefa so e considerada concluida quando:

- [ ] Cada responsabilidade permanece isolada.
- [ ] Nenhum arquivo virou um "arquivo deposito".
- [ ] A alteracao exigiu a leitura apenas dos arquivos realmente envolvidos.
- [ ] A estrutura do projeto continua modular.
- [ ] O codigo permanece organizado para futuras manutencoes.
- [ ] A proxima IA conseguira entender e modificar apenas aquela parte do sistema sem precisar analisar centenas ou milhares de linhas desnecessariamente.

---

**Na duvida entre criar um arquivo novo ou aumentar um existente: crie o novo**, desde que ele represente uma responsabilidade clara e unica.

## Debitos conhecidos

Arquivos que ja violam esta constituicao. Ao mexer neles, **quebre antes** em vez de aumentar. Nao quebre "de passagem" numa tarefa que nao os envolve - e mudanca estrutural e merece commit proprio.

| Arquivo | Linhas | Situacao |
|---------|--------|----------|
| `IA.md` | ~360 | Crescimento esperado (append-only). Passando de 400, mover registros antigos **sem editar** para `docs/ia-archive/IA-ARCHIVE-<ano>.md` com ponteiro datado. Nunca apagar. |

Resolvido em 2026-07-29: `start_app.py` tinha 1716 linhas com seis
responsabilidades. Virou gatilho de 48 linhas + o pacote `scripts/hud/`,
com 18 modulos - o maior tem 280.
