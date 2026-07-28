# 🤖 IA.md — Contexto Operacional do Projeto Meu Ecoo Prisma

> Arquivo de memória técnica do projeto, criado a partir do `TEMPLATE-CONTEXTO-IA.md` do Felixo System Design.
> **Regra de preservação histórica**: não apague nem reescreva registros antigos; adicione entradas novas datadas com contexto, motivo e validação.

---

## 🎯 OBJETIVO DO PROJETO

[2026-07-16] Plataforma SaaS de estudos para instituições de ensino usando o **OpenRouter como motor de IA**. Modelo: instituição assina → recebe créditos de IA → diretor distribui para professores (gerar/corrigir provas e material) e alunos (tutor com **memória persistente**). Três perfis de login: aluno, professor, diretor. Detalhes em [`docs/VISAO-DO-PRODUTO.md`](docs/VISAO-DO-PRODUTO.md).

---

## 🏁 METAS & MILESTONES

- [2026-07-16] ✅ — Documentação de concepção completa (visão, arquitetura, perfis, créditos, memória, roadmap)
- [2026-07-16] ⬜ — Fase 0: fundação do monorepo (backend Django + frontend React) com `start_app.py` e login dos 3 perfis
- [2026-07-16] ⬜ — Fase 1: gateway OpenRouter + módulo de créditos + primeira ferramenta de IA

Roadmap completo em [`docs/ROADMAP.md`](docs/ROADMAP.md).

---

## 🧱 STACK & ARQUITETURA

[2026-07-16] Stack planejada (alinhada ao Felixo System Design): React + TypeScript + Tailwind (Vite) no frontend; Django + DRF no backend (monolito modular: apps `contas`, `academico`, `conteudo`, `creditos`, `ia`, `memoria`); PostgreSQL; deploy no Railway. Toda chamada de IA passa pelo gateway do backend — frontend nunca fala com o OpenRouter. Detalhes em [`docs/ARQUITETURA-DO-SISTEMA.md`](docs/ARQUITETURA-DO-SISTEMA.md).

---

## 📌 DECISÕES TÉCNICAS

- [2026-07-16] **OpenRouter como provedor único de IA** — API unificada multi-modelo permite roteamento por classe de tarefa (tutoria, geração, correção, resumo) otimizando custo dos créditos. Mapeamento classe→modelo em configuração, não em código.
- [2026-07-16] **Crédito como unidade interna** — conversão custo-do-modelo→créditos por tabela configurável com margem; saldo derivado do ledger (fonte única), débito só após resposta bem-sucedida. Ver [`docs/CREDITOS-E-ASSINATURAS.md`](docs/CREDITOS-E-ASSINATURAS.md).
- [2026-07-16] **Memória por resumos consolidados, não conversa crua** — sessões são resumidas por modelo barato em registros imutáveis datados; recuperação simples (matéria/tópico/recência) antes de considerar embeddings. Ver [`docs/MEMORIA-PERSISTENTE.md`](docs/MEMORIA-PERSISTENTE.md).
- [2026-07-16] **Monolito modular primeiro** — sem microserviços/fila/cache até gargalo real (princípio "simplicidade verificável" do `GUIA_MINIMO_QUALIDADE.md`).
- [2026-07-16] **Conteúdo de IA nasce rascunho** — prova/nota só vale após revisão explícita do professor (decisão pedagógica e de responsabilidade).

---

## 🐛 BUGS RESOLVIDOS

_Nenhum ainda — projeto em fase de documentação._

---

## 🧪 TESTES & VALIDAÇÕES

_Nenhum ainda — sem código de aplicação._

---

## 🔌 INTEGRAÇÕES EXTERNAS

- [2026-07-16] **OpenRouter** (planejada) — chave única da plataforma, server-side, via variável de ambiente. Nunca no frontend nem no repositório.

---

## 📓 REGISTRO DE SESSÕES

- [2026-07-16] Sessão inicial: criada toda a documentação de concepção seguindo o padrão Felixo System Design — `README.md` reescrito no padrão `DESIGN_SYSTEM_README.md`; criados `docs/VISAO-DO-PRODUTO.md`, `docs/ARQUITETURA-DO-SISTEMA.md`, `docs/PERFIS-E-PERMISSOES.md`, `docs/CREDITOS-E-ASSINATURAS.md`, `docs/MEMORIA-PERSISTENTE.md`, `docs/ROADMAP.md` e este `IA.md`. Próximo passo: Fase 0 do roadmap.
- [2026-07-28] Projeto renomeado de "Estudo com IA" para "Meu Ecoo Prisma": repositório GitHub renomeado (`flaviavs-commits/Meu-Ecoo-Prisma`), remote local atualizado e todas as referências ao nome antigo substituídas em `README.md`, `IA.md`, `docs/*.md` e `mockup/*.html`. Corrigido também um link quebrado no README que apontava para a pasta local `Padrão de qualidade - Felixo System Design/` (ignorada pelo git, portanto inválida para quem clona o repositório).
