# E15 — Limite percentual e API do aluno

**Status:** CONCLUÍDA localmente
**Responsável:** Code Review
**Depende de:** E04, E06, E07, E10
**Escopo:** regra de uso de IA por conta, catálogo de planos institucionais e
primeira API de aluno para tutor, materiais, simulados, agenda e dashboard.

## Decisão de negócio

A unidade comercial é a conta ativa da instituição. O valor mensal é:

```text
preço do plano × (alunos ativos + professores ativos + diretores ativos)
```

Todas as contas acadêmicas de uma instituição recebem o mesmo limite percentual
do plano contratado. O consumo é append-only e contado em percentual; não há
saldo individual nem distribuição manual de créditos no novo fluxo.

O limite vale **por competência mensal** (`YYYY-MM`, mês-calendário em UTC),
espelhando a cobrança. Cada `ConsumoIA` grava a competência no débito e o
limite é sempre lido dentro da janela aberta — sem isso, a conta que esgotasse
o percentual num mês ficaria bloqueada nos meses seguintes com a escola sendo
cobrada de novo. A regra está isolada em `backend/limites/ciclo.py`.

Catálogo inicial:

| Plano | Preço por conta/mês | Limite por conta |
|---|---:|---:|
| Prisma | R$ 68,97 | 100% |
| Prisma Pro | R$ 78,97 | 171% |
| Prisma Ultra | R$ 88,97 | 271% |

O tier interno `VITIS_SOULS` é mantenedor da plataforma e não recebe plano
comercial. Apenas contas acadêmicas ativas entram no cálculo da cobrança.

## Entrega backend

- `limites` cria `PlanoInstitucional`, `AssinaturaInstituicao`, `CotaUsuario`
  (trava transacional) e `ConsumoIA` append-only.
- O gateway converte o custo de cada fornecedor em percentual e registra
  fornecedor/modelo/tarefa. Quem recusa é o **portão** (`autorizar_uso`), antes
  da chamada; o débito nunca recusa, porque só chega depois de o provedor ter
  cobrado. O estouro máximo é de uma chamada, e ela bloqueia a próxima.
- Uma chamada de IA por conta de cada vez (`409 chamada_em_andamento`). Sem esse
  teto, chamadas simultâneas passariam pelo portão juntas — nenhuma debitou
  ainda — e o estouro seria do tamanho da concorrência.
- A mesma referência de chamada é idempotente: retry não cria segundo consumo.
- O mantenedor pode trocar o plano de uma escola com motivo obrigatório e
  auditoria; a Vitis Souls é protegida contra plano comercial.
- O app `aluno` expõe dashboard e agenda com isolamento pelo usuário e tenant.
- `memoria` expõe conversa do tutor e configuração de estilo, dificuldade,
  foco de prova e tamanho da resposta.
- `conteudo` expõe materiais gerados, simulados e respostas/finalização com
  gabarito oculto enquanto o simulado está aberto.

## Contratos

Os endpoints e exemplos de payload estão em
[`../contratos/API-ALUNO-E-LIMITES.md`](../contratos/API-ALUNO-E-LIMITES.md).
As rotas acadêmicas exigem JWT e não aceitam identificadores de outro tenant.

## Limites conhecidos

- O provedor OpenRouter ainda é um adaptador sem chamada de rede; o ambiente de
  teste e o de desenvolvimento usam o provedor falso, que agora honra o
  contrato de saída estruturada do simulado (`ia/provedores/roteiros.py`).
- A correção comentada por questão ainda não é persistida: `correcao_comentada`
  chega ao prompt, mas `QuestaoSimulado` não tem campo para o comentário.
- A retenção da conversa bruta continua pendente de decisão LGPD em E07.
- O app `creditos` e suas migrações antigas permanecem instalados apenas como
  compatibilidade histórica. O novo gateway, o painel de instituição e a API do
  aluno usam exclusivamente percentuais; a remoção física do legado é uma
  etapa separada para não apagar histórico sem plano de migração.
- Os textos de placeholders em `frontend/app/aluno.html` ainda precisam ser
  ligados às rotas e substituir referências editoriais antigas a créditos; isso
  não bloqueia a validação do contrato backend.

## Correção pós-revisão (2026-08-05)

A revisão de `docs/REVISAO-2026-08-05-COMMITS-DO-DIA.md` encontrou dois
bloqueantes nesta etapa, ambos corrigidos:

- **Limite vitalício:** `estado_cota` somava todo o `ConsumoIA` desde sempre.
  Corrigido com a competência mensal descrita acima
  (`limites/ciclo.py`, campo `ConsumoIA.ciclo`, migração
  `limites/0003_consumo_ciclo`, que faz backfill em lote a partir de
  `criado_em`).
- **Simulado com questão fabricada:** o serviço descartava a resposta do modelo
  e criava questões genéricas com `gabarito="A"` em todas. Agora as questões
  vêm só do modelo, via contrato de saída estruturada
  (`conteudo/questoes_ia.py`); saída fora do contrato responde `503`
  `simulado_indisponivel` e não cria nada.

## Validação

- `manage.py check` sem problemas.
- `makemigrations --check --dry-run --noinput` sem mudanças pendentes.
- `git diff --check` sem saída.
- Suíte backend em SQLite: `218 passed, 3 skipped` (eram `189 passed, 3
  skipped` antes das correções).
- Suíte backend em **PostgreSQL: `221 passed`, zero skips** — os testes de
  concorrência rodaram pela primeira vez. Até então
  `limites/tests/test_concorrencia.py` sequer conseguia executar: pedia
  fixtures que só existiam dentro de `test_cota.py`, e o `skipif` de SQLite
  escondia o erro. Corrigido com `limites/tests/conftest.py` e
  `serialized_rollback=True` nos módulos transacionais, que sem isso levavam o
  catálogo de planos junto no flush.

**Estado final:** CONCLUÍDA localmente, com os dois bloqueantes da revisão
corrigidos; aguardando apenas a integração do frontend e a validação remota do
deployment. Identidade: **Code review**.
