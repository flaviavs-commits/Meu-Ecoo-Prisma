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
- O gateway converte o custo de cada fornecedor em percentual, registra
  fornecedor/modelo/tarefa e rejeita um débito que ultrapasse o limite restante.
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
  teste usa o provedor falso.
- A geração de questões do simulado é determinística até existir um contrato de
  saída estruturada entre o gateway e o provedor real.
- A retenção da conversa bruta continua pendente de decisão LGPD em E07.
- O app `creditos` e suas migrações antigas permanecem instalados apenas como
  compatibilidade histórica. O novo gateway, o painel de instituição e a API do
  aluno usam exclusivamente percentuais; a remoção física do legado é uma
  etapa separada para não apagar histórico sem plano de migração.
- Os textos de placeholders em `frontend/app/aluno.html` ainda precisam ser
  ligados às rotas e substituir referências editoriais antigas a créditos; isso
  não bloqueia a validação do contrato backend.

## Validação

- `manage.py check` sem problemas.
- `makemigrations --check --dry-run --noinput` sem mudanças pendentes.
- Suíte backend em SQLite: `189 passed, 3 skipped`.
- O teste de concorrência de limites é executado somente em PostgreSQL; em
  SQLite ele é explicitamente pulado porque o banco bloqueia a tabela inteira.

**Estado final:** CONCLUÍDA localmente; aguardando apenas a integração do
frontend e a validação remota do deployment. Identidade: **Code Review**.
