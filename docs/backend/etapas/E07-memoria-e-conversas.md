# E07 - Memoria e conversas do tutor

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
> **Depende de:** E06 · **Destrava:** -
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Dar memoria ao tutor: guardar a conversa do aluno e manter um resumo que evolui,
para que o tutor lembre do que aquele aluno ja estudou sem reenviar a conversa
inteira a cada mensagem.

**Esta etapa lida com o dado mais sensivel do sistema.** Leia o
[contrato de LGPD](../contratos/LGPD-E-DADOS-SENSIVEIS.md) antes de escrever
qualquer linha.

## 2. Pre-requisitos

- E06 `CONCLUIDA` (gateway de IA disponivel)
- [`../contratos/LGPD-E-DADOS-SENSIVEIS.md`](../contratos/LGPD-E-DADOS-SENSIVEIS.md), item 4
- A tela do tutor em `mockup/aluno.html` - e a melhor especificacao funcional

## 3. Escopo

**Entra:** persistencia da conversa, memoria consolidada, consolidacao e
compactacao, recuperacao do contexto para o tutor, controle de acesso.

**Nao entra:** a interface do tutor (frontend) e embeddings / busca semantica -
ver item 4.

## 4. Decisoes ja travadas - nao reabrir

| Decisao | Valor |
|---------|-------|
| Conversa bruta | **E persistida** em banco |
| Memoria | Resumo consolidado que **e compactado com o tempo** |
| Recuperacao | Simples primeiro: materia, topico, recencia. **Sem embeddings** ate haver necessidade demonstrada. |
| Consolidacao | Feita por modelo barato, via gateway de E06 |
| Imutabilidade | Registro de memoria consolidada e datado e imutavel |

> Isto **refina** o registro de 2026-07-16 do [`IA.md`](../../../IA.md), que
> dizia "memoria por resumos consolidados, nao conversa crua". Hoje os dois
> coexistem: log bruto **e** memoria que evolui. Se voce achar contradicao entre
> os documentos, esta e a versao atual.

## 5. Como fazer

### 5.1 Tres entidades, tres papeis

```text
Conversa            uma sessao de estudo do aluno com o tutor
  └── Mensagem      cada turno (aluno ou tutor), na ordem
MemoriaConsolidada  resumo datado e imutavel do que aquele aluno estudou
```

Sao separadas de proposito. A conversa e log; a memoria e conhecimento. Elas tem
ciclo de vida, acesso e prazo de retencao diferentes - juntar as duas
inviabilizaria apagar uma sem perder a outra.

`Mensagem` guarda `papel` (`ALUNO` / `TUTOR`), `conteudo`, `criado_em`, e a
referencia a `ChamadaIA` que a gerou, quando for do tutor.

`MemoriaConsolidada` guarda `aluno`, `disciplina`/`topico`, `resumo`,
`periodo_inicio`, `periodo_fim`, `criado_em`. **Nunca sofre `UPDATE`** -
consolidar de novo cria um registro novo que substitui logicamente o anterior.

### 5.2 O ciclo de vida

```text
aluno conversa      -> Mensagem (bruto)
sessao encerra      -> consolidacao gera MemoriaConsolidada
tempo passa         -> varias memorias viram uma memoria mais compacta
tutor e chamado     -> recupera memoria relevante + ultimas mensagens
```

A consolidacao **consome credito** - e uma chamada de IA como qualquer outra, via
gateway de E06. Decida e registre: consolidar debita do aluno ou da instituicao?
E trabalho de sistema, nao pedido do aluno. **Recomendacao:** debitar da
instituicao, e registrar a decisao.

### 5.3 Recuperacao - simples de proposito

Ao montar o contexto do tutor: filtre por aluno, disciplina e topico; ordene por
recencia; limite por quantidade.

**Nao introduza embeddings, banco vetorial ou busca semantica nesta etapa.** A
decisao de comecar simples e explicita. Se a recuperacao simples se mostrar
insuficiente, isso e um achado a registrar com evidencia - nao uma licenca para
adicionar a dependencia por conta propria.

Ha um teto de contexto: nunca envie ao provedor tudo o que existe. Defina um
orcamento de tokens e respeite - senao cada mensagem fica mais cara que a
anterior, indefinidamente.

### 5.4 Acesso - o ponto mais delicado

Da matriz de E04:

| Quem | Pode ler a conversa crua |
|------|--------------------------|
| O proprio aluno | sim |
| Professor | **nao** |
| Diretor | **nao** |
| Equipe interna | **nao** por padrao |

O que sobe para professor e diretor e **agregado** (usou o tutor X vezes, temas
mais buscados), nunca o texto.

Se um dia existir acesso individual justificado, ele passa pelo mixin de acao
destrutiva de E04: motivo obrigatorio e auditoria. **Nao implemente esse acesso
agora.**

Um adolescente conversando com um tutor de IA sobre o que nao entende revela
dificuldade e, as vezes, muito mais. Tratar isso como log comum seria erro
grave.

### 5.5 Retencao - pendencia aberta

Por quanto tempo a conversa bruta fica guardada? **Nao ha decisao ainda.**

Nao invente um prazo. Faca assim:

- modele o campo/mecanismo que permite aplicar um prazo depois;
- **nao apague nada** ate haver decisao;
- registre a pergunta no diario e marque como `AGUARDANDO DECISAO` se for
  bloquear a entrega.

A memoria consolidada tende a ter prazo maior que o bruto - ela e o valor do
produto; o bruto e o rastro.

### 5.6 TDD - ordem sugerida

1. Conversa guarda mensagens na ordem.
2. Consolidacao gera memoria e nao altera o bruto.
3. Consolidacao debita credito via gateway.
4. Recuperacao traz o relevante e respeita o teto de contexto.
5. Compactacao de varias memorias gera uma nova, sem apagar as originais.
6. Professor recebe 403 ao tentar ler conversa de aluno.
7. Diretor recebe 403 ao tentar ler conversa de aluno.
8. Aluno de outra instituicao -> 404.
9. Nenhum conteudo de mensagem aparece em log.
10. `MemoriaConsolidada` recusa `UPDATE`.

## 6. Contrato de saida

- `memoria.Conversa`, `memoria.Mensagem`, `memoria.MemoriaConsolidada` migrados
- servico de consolidacao usando o gateway de E06
- servico de recuperacao de contexto com teto de tokens
- acesso restrito conforme a matriz
- mecanismo de retencao preparado, sem prazo aplicado

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Conversa de menor exposta | Acesso restrito + teste que prova o 403 |
| Contexto crescendo sem limite | Orcamento de tokens explicito |
| Consolidacao gastando credito sem controle | Passa pelo gateway; decisao de quem paga registrada |
| Prazo de retencao indefinido | **Pendencia aberta.** Nao apagar nada ate decidir. |
| Tentacao de adicionar banco vetorial | Decisao explicita de comecar simples |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

_(vazio - primeira entrada e sua)_

## 9. Criterio de pronto

- [ ] Os 10 testes do item 5.6 passam - saida real no diario
- [ ] Professor e diretor **nao** leem conversa crua - testado
- [ ] Nenhum conteudo de mensagem em log - verificado
- [ ] Teto de contexto aplicado e testado
- [ ] `MemoriaConsolidada` imutavel por excecao
- [ ] Decisao de quem paga a consolidacao registrada
- [ ] Pendencia de retencao registrada no diario **e** no `IA.md`
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] Commit feito, so com arquivos desta etapa
