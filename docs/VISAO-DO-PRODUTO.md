# 🎯 VISÃO DO PRODUTO — Meu Ecoo Prisma

> **O que é**: Documento de visão do produto — problema, público, proposta de valor e escopo.
>
> **Quando usar**: Antes de qualquer decisão de feature ou arquitetura. É a fonte única do "porquê" do projeto.
>
> **Documentos relacionados**: [ARQUITETURA-DO-SISTEMA.md](ARQUITETURA-DO-SISTEMA.md) • [PERFIS-E-PERMISSOES.md](PERFIS-E-PERMISSOES.md) • [CREDITOS-E-ASSINATURAS.md](CREDITOS-E-ASSINATURAS.md)

---

## 📋 Índice

- [1. Problema](#1-problema)
- [2. Solução](#2-solução)
- [3. Público-alvo](#3-público-alvo)
- [4. Proposta de valor](#4-proposta-de-valor)
- [5. Escopo do MVP](#5-escopo-do-mvp)
- [6. Fora de escopo (por enquanto)](#6-fora-de-escopo-por-enquanto)
- [7. Métricas de sucesso](#7-métricas-de-sucesso)

---

## 1. Problema

Instituições de ensino querem usar IA no dia a dia pedagógico, mas enfrentam três barreiras:

1. **Custo imprevisível** — dar uma assinatura individual de IA (ChatGPT, Claude, etc.) para cada aluno e professor é caro e sem controle centralizado.
2. **Ferramentas genéricas** — os chats de IA não conhecem o contexto escolar: turmas, matérias, provas, notas, faltas. Cada uso começa do zero.
3. **Sem memória pedagógica** — a IA não lembra o histórico do aluno; não há continuidade entre uma sessão de estudo e a próxima, nem visão de progresso para professores e direção.

## 2. Solução

Uma **plataforma única por instituição**, com o **OpenRouter como motor de IA**:

- A instituição **assina a plataforma** e recebe um pool de **créditos de IA** (modelo análogo a Claude/Codex: assinatura → créditos → consumo).
- Os créditos são **distribuídos** entre professores (gerar/corrigir conteúdo) e alunos (estudar).
- Cada aluno tem **memória persistente**: a IA lembra o que ele estudou, onde tem dificuldade e como evoluiu.
- Toda a produção (provas, textos, materiais, correções) fica **armazenada** na plataforma, junto com **notas, faltas e desempenho**.

## 3. Público-alvo

| Segmento | Papel na plataforma |
|----------|--------------------|
| Escolas de ensino fundamental e médio | Cliente principal do MVP |
| Cursos livres e cursinhos | Mesmo modelo, turmas mais fluidas |
| Faculdades / universidades | Fase posterior (escala e integrações maiores) |

Usuários finais: **alunos**, **professores** e **diretores/coordenação** — cada um com login e ferramentas próprias ([PERFIS-E-PERMISSOES.md](PERFIS-E-PERMISSOES.md)).

## 4. Proposta de valor

- **Para a instituição**: um único contrato, custo previsível, controle total do uso de IA e dados pedagógicos centralizados.
- **Para o professor**: horas de trabalho economizadas em elaboração e correção de provas e material didático.
- **Para o aluno**: um tutor de IA pessoal que **lembra dele** — não um chat genérico.
- **Diferencial técnico**: OpenRouter permite escolher o modelo certo por tarefa (barato para rascunho, forte para correção), otimizando o custo dos créditos.

## 5. Escopo do MVP

1. **Autenticação com 3 perfis** (aluno, professor, diretor) vinculados a uma instituição
2. **Chat de estudo com memória persistente** por aluno
3. **Gerador e corretor de provas** para professores
4. **Gerador de textos de estudo/trabalho**
5. **Registro de notas e faltas** + dashboards básicos de desempenho
6. **Sistema de créditos**: pool da instituição, cotas por perfil, contabilidade por requisição
7. **Armazenamento de conteúdo** gerado (acervo da instituição)

## 6. Fora de escopo (por enquanto)

- App mobile nativo (o MVP é web responsivo)
- Integração com sistemas acadêmicos externos (ERP escolar, Google Classroom)
- Pagamento self-service (assinatura fechada comercialmente no início)
- Geração de conteúdo multimídia (áudio/vídeo)
- Proctoring / antifraude de provas online

## 7. Métricas de sucesso

- **Adoção**: % de alunos ativos por semana na instituição piloto
- **Valor para professor**: provas geradas/corrigidas por professor por mês
- **Eficiência de créditos**: custo médio (em créditos) por sessão de estudo e por prova corrigida
- **Continuidade**: % de sessões de estudo que reaproveitam memória de sessões anteriores

---

> **Assinatura de Origem**
> Documento do projeto **Meu Ecoo Prisma**, seguindo o padrão do **Felixo System Design**.
> Data desta versão: 2026-07-16
