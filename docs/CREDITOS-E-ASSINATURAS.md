# 💳 CRÉDITOS E ASSINATURAS — Meu Ecoo Prisma

> **O que é**: O modelo econômico da plataforma — assinatura por instituição, pool de créditos de IA, cotas por perfil e contabilidade de consumo.
>
> **Quando usar**: Ao implementar o módulo `creditos` e qualquer ferramenta que consuma IA.
>
> **Documentos relacionados**: [ARQUITETURA-DO-SISTEMA.md](ARQUITETURA-DO-SISTEMA.md) • [PERFIS-E-PERMISSOES.md](PERFIS-E-PERMISSOES.md)

---

## 📋 Índice

- [1. Modelo geral](#1-modelo-geral)
- [2. O que é um crédito](#2-o-que-é-um-crédito)
- [3. Planos de assinatura](#3-planos-de-assinatura)
- [4. Distribuição: pool → cotas](#4-distribuição-pool--cotas)
- [5. Contabilidade (ledger)](#5-contabilidade-ledger)
- [6. Políticas de limite](#6-políticas-de-limite)
- [7. Otimização de custo via OpenRouter](#7-otimização-de-custo-via-openrouter)

---

## 1. Modelo geral

O modelo segue o padrão consolidado por Claude, Codex e similares: **assinatura → créditos → consumo medido**.

```
Assinatura mensal da instituição
        │
        ▼
Pool de créditos da instituição (renova a cada ciclo)
        │  distribuído pelo diretor
        ▼
Cotas por perfil / turma / usuário
        │  consumido a cada chamada de IA
        ▼
Ledger de consumo (auditável, por usuário e ferramenta)
```

## 2. O que é um crédito

- **Crédito** é a unidade interna de consumo de IA da plataforma.
- Cada chamada ao OpenRouter retorna o uso real de tokens; o gateway converte **custo em dólares do modelo → créditos** por uma tabela de conversão configurável (com margem operacional).
- A conversão fica em **configuração versionada**, nunca hardcoded — trocar de modelo ou repactuar margem não exige mudança de código.
- Para o usuário final, a interface mostra créditos e estimativas simples ("esta prova custou ~3 créditos"), nunca tokens crus.

## 3. Planos de assinatura

Estrutura de referência (valores comerciais definidos fora deste documento):

| Plano | Público | Inclui |
|-------|---------|--------|
| **Essencial** | Escolas pequenas / cursos | Pool base de créditos, todos os perfis, ferramentas do MVP |
| **Institucional** | Escolas médias/grandes | Pool maior, dashboards avançados, prioridade de suporte |
| **Rede** | Redes de ensino | Multi-unidade, pool compartilhado ou por unidade, relatórios consolidados |

- Créditos do pool **renovam por ciclo** (mensal); política de acúmulo/expiração é configuração do plano.
- **Créditos extras avulsos** podem ser adquiridos quando o pool esgota antes do ciclo.

## 4. Distribuição: pool → cotas

O **diretor** distribui o pool:

- **Cota padrão por perfil** (ex.: X créditos/mês por aluno, Y por professor) — aplicada automaticamente a novos usuários.
- **Ajustes finos**: cota maior para uma turma em semana de provas, ou para um professor produzindo material.
- **Reserva institucional**: parte do pool não distribuída, para remanejamento durante o ciclo.

Regras:

1. A soma das cotas pode exceder o pool (overbooking controlado), mas o **pool é o teto real**: esgotou, todas as chamadas param com aviso claro.
2. Mudança de cota vale a partir do momento da alteração e fica registrada na auditoria.

## 5. Contabilidade (ledger)

Toda movimentação é um lançamento imutável:

| Campo | Exemplo |
|-------|---------|
| Quem | usuário (e perfil) |
| O quê | ferramenta (`tutor`, `gerar_prova`, `corrigir_prova`, …) |
| Modelo | modelo OpenRouter efetivamente usado |
| Tokens | entrada/saída reportados pelo OpenRouter |
| Créditos | valor debitado após conversão |
| Quando | timestamp |

- **Débito só após resposta bem-sucedida**; falha do provedor não consome crédito do usuário.
- O ledger alimenta os relatórios do diretor e a barra de saldo de cada usuário.
- Saldo de cota é **derivado do ledger** (fonte única de verdade), não um contador paralelo.

## 6. Políticas de limite

- **Verificação antes da chamada**: sem saldo na cota (ou no pool), a requisição é bloqueada **antes** de chamar o OpenRouter, com mensagem clara e orientação ("peça mais créditos ao diretor").
- **Alertas**: usuário avisado a 80% da cota; diretor avisado a 80% do pool.
- **Rate limiting** por usuário (chamadas/minuto) para prevenir abuso e estouro acidental.
- **Modo econômico** (opcional, por instituição): quando o pool passa de um limiar, o roteamento troca para modelos mais baratos automaticamente.

## 7. Otimização de custo via OpenRouter

- O roteamento classe-de-tarefa → modelo ([arquitetura, §3](ARQUITETURA-DO-SISTEMA.md#3-integração-com-o-openrouter)) é a principal alavanca de custo: tarefas simples usam modelos baratos.
- Prompts com partes estáveis (instruções da ferramenta, memória consolidada) são estruturados para aproveitar **cache de prompt** quando o modelo suportar.
- Relatórios de custo por ferramenta permitem recalibrar a tabela de conversão e o roteamento com dados reais.

---

> **Assinatura de Origem**
> Documento do projeto **Meu Ecoo Prisma**, seguindo o padrão do **Felixo System Design**.
> Data desta versão: 2026-07-16
