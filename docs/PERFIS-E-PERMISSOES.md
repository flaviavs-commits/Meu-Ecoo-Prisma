# 👥 PERFIS E PERMISSÕES — Meu Ecoo Prisma

> **O que é**: Definição dos três perfis de acesso (aluno, professor, diretor), suas ferramentas e o mapa de permissões.
>
> **Quando usar**: Ao implementar autenticação, rotas, telas e qualquer verificação de autorização.
>
> **Documentos relacionados**: [VISAO-DO-PRODUTO.md](VISAO-DO-PRODUTO.md) • [ARQUITETURA-DO-SISTEMA.md](ARQUITETURA-DO-SISTEMA.md) • [CREDITOS-E-ASSINATURAS.md](CREDITOS-E-ASSINATURAS.md)

---

## 📋 Índice

- [1. Modelo de acesso](#1-modelo-de-acesso)
- [2. Perfil Aluno](#2-perfil-aluno-)
- [3. Perfil Professor](#3-perfil-professor-)
- [4. Perfil Diretor](#4-perfil-diretor-)
- [5. Matriz de permissões](#5-matriz-de-permissões)
- [6. Regras transversais](#6-regras-transversais)

---

## 1. Modelo de acesso

- **Um login, um perfil, uma instituição.** Todo usuário pertence a exatamente uma instituição e tem um perfil: `aluno`, `professor` ou `diretor`.
- A tela de login oferece as **3 opções de entrada**; após autenticar, o usuário cai na área do seu perfil (`/aluno`, `/professor`, `/diretor`).
- Contas são criadas pelo diretor (ou por convite emitido por ele) — não há cadastro aberto ao público.

## 2. Perfil Aluno 🧑‍🎓

**Foco: estudar com IA e acompanhar o próprio desempenho.**

| Ferramenta | Descrição |
|------------|-----------|
| **Tutor de estudo** | Chat de IA com [memória persistente](MEMORIA-PERSISTENTE.md): lembra matérias, dificuldades e progresso entre sessões |
| **Gerador de texto de estudo** | Resumos, explicações e textos-base para estudo e trabalhos, a partir do conteúdo das matérias |
| **Simulados** | Provas de treino geradas por IA com correção automática e feedback |
| **Minhas notas e faltas** | Visualização do próprio boletim, frequência e evolução |
| **Meu saldo de créditos** | Quanto da sua cota de IA já foi usada no período |

## 3. Perfil Professor 🧑‍🏫

**Foco: produzir conteúdo pedagógico e avaliar.**

| Ferramenta | Descrição |
|------------|-----------|
| **Gerador de provas** | Cria provas por matéria/tópico/dificuldade; professor revisa e ajusta antes de publicar |
| **Correção com IA** | Corrige respostas (objetivas e dissertativas) com rubrica; professor valida a nota final |
| **Banco de conteúdo** | Acervo de provas, materiais e textos da instituição; reutilização e versionamento |
| **Gerador de material didático** | Textos, listas de exercícios e planos de aula |
| **Notas e faltas** | Lançamento por turma; painel de desempenho dos seus alunos |
| **Meu saldo de créditos** | Cota própria de créditos de geração/correção |

**Regra pedagógica**: conteúdo gerado por IA nasce como **rascunho** — só vale (prova publicada, nota lançada) após revisão explícita do professor.

## 4. Perfil Diretor 🏛️

**Foco: administrar a instituição e os créditos.**

| Ferramenta | Descrição |
|------------|-----------|
| **Gestão de usuários** | Criar/convidar/desativar alunos e professores; organizar turmas e matérias |
| **Dashboards institucionais** | Notas, faltas e desempenho por turma, matéria e período |
| **Gestão de créditos** | Ver o pool da assinatura, definir cotas por perfil/turma, acompanhar consumo ([detalhes](CREDITOS-E-ASSINATURAS.md)) |
| **Relatórios de uso de IA** | Quais ferramentas são mais usadas, por quem, com qual custo |
| **Configurações da instituição** | Períodos letivos, escala de notas, políticas de uso |

## 5. Matriz de permissões

| Ação | Aluno | Professor | Diretor |
|------|:-----:|:---------:|:-------:|
| Usar tutor de estudo com memória | ✅ | — | — |
| Gerar texto de estudo/trabalho | ✅ | ✅ | — |
| Gerar simulado para si | ✅ | — | — |
| Gerar/publicar prova | — | ✅ | — |
| Corrigir prova com IA | — | ✅ | — |
| Lançar notas e faltas | — | ✅ | — |
| Ver as próprias notas/faltas | ✅ | — | — |
| Ver notas/faltas das suas turmas | — | ✅ | ✅ |
| Ver dashboards da instituição inteira | — | — | ✅ |
| Gerenciar usuários e turmas | — | — | ✅ |
| Distribuir/monitorar créditos | — | — | ✅ |
| Ver o próprio saldo de créditos | ✅ | ✅ | ✅ |

## 6. Regras transversais

- **Autorização no backend**: cada rota valida o perfil — a interface esconder um botão não é controle de acesso.
- **Escopo institucional**: nenhum perfil enxerga dados de outra instituição.
- **Privacidade entre alunos**: aluno nunca vê nota, falta ou memória de outro aluno.
- **Auditoria**: ações administrativas (criação de usuário, mudança de cota, publicação de prova) geram registro de auditoria.

---

> **Assinatura de Origem**
> Documento do projeto **Meu Ecoo Prisma**, seguindo o padrão do **Felixo System Design**.
> Data desta versão: 2026-07-16
