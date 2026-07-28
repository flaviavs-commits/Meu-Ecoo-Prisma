# 🗺️ ROADMAP — Meu Ecoo Prisma

> **O que é**: Plano de implementação em fases, com entregáveis e critérios de pronto.
>
> **Quando usar**: Para decidir o que implementar a seguir e avaliar se uma fase terminou. Progresso real e desvios são registrados no [`IA.md`](../IA.md).
>
> **Documentos relacionados**: [VISAO-DO-PRODUTO.md](VISAO-DO-PRODUTO.md) • [ARQUITETURA-DO-SISTEMA.md](ARQUITETURA-DO-SISTEMA.md)

---

## 📋 Índice

- [Fase 0 — Fundação](#fase-0--fundação)
- [Fase 1 — Núcleo de IA com créditos](#fase-1--núcleo-de-ia-com-créditos)
- [Fase 2 — Ferramentas do professor](#fase-2--ferramentas-do-professor)
- [Fase 3 — Memória persistente e tutor completo](#fase-3--memória-persistente-e-tutor-completo)
- [Fase 4 — Gestão institucional](#fase-4--gestão-institucional)
- [Fase 5 — Piloto](#fase-5--piloto)
- [Ideias para expansão futura](#ideias-para-expansão-futura)

---

## Fase 0 — Fundação

**Objetivo**: repositório pronto para desenvolvimento com o padrão de qualidade aplicado.

- ⬜ Estrutura do monorepo (`backend/` Django + `frontend/` React/Vite/TS)
- ⬜ `start_app.py` na raiz (menu interativo: instalar, configurar, iniciar) — obrigatório pelo `GUIA-START-APP-SCRIPT.md`
- ⬜ Autenticação JWT com os 3 perfis e vínculo com instituição
- ⬜ CI básico (lint + testes)

**Pronto quando**: um dev clona, roda `python start_app.py` e sobe frontend + backend com login funcionando para os 3 perfis.

## Fase 1 — Núcleo de IA com créditos

**Objetivo**: primeira chamada de IA de ponta a ponta, já medida.

- ⬜ Gateway OpenRouter (`ia`): chave server-side, roteamento classe→modelo por configuração, streaming
- ⬜ Módulo `creditos`: pool, cotas por perfil, ledger, bloqueio pré-chamada
- ⬜ Primeira ferramenta: **gerador de texto de estudo** (aluno e professor)
- ⬜ Barra de saldo de créditos na interface

**Pronto quando**: gerar um texto debita créditos corretos no ledger e o saldo reflete na tela.

## Fase 2 — Ferramentas do professor

**Objetivo**: valor imediato para o professor.

- ⬜ Gerador de provas (rascunho → revisão → publicação)
- ⬜ Correção com IA + validação do professor
- ⬜ Banco de conteúdo (acervo institucional)
- ⬜ Lançamento de notas e faltas por turma

**Pronto quando**: um professor cria, aplica e corrige uma prova inteira na plataforma.

## Fase 3 — Memória persistente e tutor completo

**Objetivo**: o diferencial do produto para o aluno.

- ⬜ Módulo `memoria` (recuperação, injeção, consolidação por modelo barato)
- ⬜ Tutor de estudo com memória entre sessões
- ⬜ Simulados com correção automática alimentando o domínio por tópico
- ⬜ Tela "minha memória" (transparência e exclusão)

**Pronto quando**: uma segunda sessão de estudo demonstra usar contexto da primeira.

## Fase 4 — Gestão institucional

**Objetivo**: o diretor administra tudo pela plataforma.

- ⬜ Gestão de usuários, turmas e matérias
- ⬜ Dashboards de notas, faltas e desempenho
- ⬜ Painel de créditos (distribuição, alertas, relatórios de uso de IA)
- ⬜ Auditoria de ações administrativas

**Pronto quando**: um ciclo mensal de créditos é distribuído, consumido e reportado sem intervenção manual.

## Fase 5 — Piloto

**Objetivo**: validar com uma instituição real.

- ⬜ Deploy em produção (Railway) com monitoramento
- ⬜ Onboarding da instituição piloto
- ⬜ Coleta das métricas de sucesso ([visão, §7](VISAO-DO-PRODUTO.md#7-métricas-de-sucesso))
- ⬜ Ajustes de roteamento/conversão de créditos com dados reais

## Ideias para expansão futura

Melhorias que o projeto poderia expandir — contribuições bem-vindas:

- App mobile / PWA
- Integração com Google Classroom e ERPs escolares
- Busca semântica (embeddings) na memória e no acervo
- Pagamento self-service e gestão de planos
- Conteúdo multimídia (áudio para acessibilidade, geração de diagramas)

---

> **Assinatura de Origem**
> Documento do projeto **Meu Ecoo Prisma**, seguindo o padrão do **Felixo System Design**.
> Data desta versão: 2026-07-16
