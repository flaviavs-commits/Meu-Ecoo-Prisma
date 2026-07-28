# 🎓 Meu Ecoo Prisma

<div align="center">

![OpenRouter](https://img.shields.io/badge/OpenRouter-Motor_de_IA-6467F2?style=for-the-badge)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![Django](https://img.shields.io/badge/Django-API_REST-0C4B33?style=for-the-badge&logo=django&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Plataforma de estudos para instituições de ensino com IA via OpenRouter, créditos por assinatura e memória persistente por aluno.**

[📖 Visão do Produto](docs/VISAO-DO-PRODUTO.md) • [🏗️ Arquitetura](docs/ARQUITETURA-DO-SISTEMA.md) • [👥 Perfis](docs/PERFIS-E-PERMISSOES.md) • [💳 Créditos](docs/CREDITOS-E-ASSINATURAS.md) • [🧠 Memória](docs/MEMORIA-PERSISTENTE.md)

</div>

---

## 📋 Índice

- [📋 Sobre o Projeto](#-sobre-o-projeto)
- [💡 **Como Funciona**](#-como-funciona) ⭐ **DESTAQUE**
- [📁 Estrutura do Repositório](#-estrutura-do-repositório)
- [📚 Documentação Completa](#-documentação-completa)
- [👥 Perfis de Acesso](#-perfis-de-acesso)
- [🛠️ Stack Planejada](#️-stack-planejada)
- [🚧 Status do Projeto](#-status-do-projeto)
- [📄 Licença](#-licença)
- [👤 Autor](#-autor)

---

## 📋 Sobre o Projeto

O **Meu Ecoo Prisma** é uma plataforma SaaS para **instituições de ensino em geral** (escolas, cursos, universidades) que usa o **OpenRouter como motor de IA**. A instituição assina a plataforma e recebe **créditos de IA** — assim como funciona em Claude, Codex e similares — que são distribuídos entre professores e alunos:

- **🧑‍🏫 Professores** geram e corrigem provas, criam material de estudo e acompanham turmas.
- **🧑‍🎓 Alunos** estudam com um tutor de IA com **memória persistente**, que lembra o histórico, as dificuldades e o progresso de cada um.
- **🏛️ Diretores** administram a instituição: distribuem créditos, monitoram notas, faltas, desempenho e uso da plataforma.

Todo o conteúdo gerado (provas, textos, resumos, correções) fica **armazenado na plataforma**, formando o acervo pedagógico da instituição.

---

## 💡 Como Funciona ⭐

> **🚀 Um motor de IA, três perfis, créditos por assinatura**
>
> **Instituição assina → recebe créditos → distribui para professores e alunos → todos usam IA com memória persistente**

### 💡 Por que usar?

- **🎯 IA sob medida por perfil**: cada login (aluno, professor, diretor) abre um conjunto próprio de ferramentas
- **🧠 Memória persistente**: a IA lembra o histórico de estudo de cada aluno entre sessões — o tutor evolui com o aluno
- **💳 Custo previsível**: créditos por assinatura, com cotas por perfil e monitoramento de consumo pelo diretor
- **🔀 Multi-modelo via OpenRouter**: um único contrato de API dá acesso a dezenas de modelos, com roteamento por custo/tarefa
- **📦 Acervo institucional**: provas, textos e materiais gerados ficam armazenados e reutilizáveis

### Ferramentas por perfil

1. **Aluno** — tutor de estudo com memória, gerador de textos de estudo e apoio a trabalhos, simulados, acompanhamento das próprias notas e faltas
2. **Professor** — geração e correção de provas com IA, banco de conteúdo, gerador de material didático, lançamento de notas e faltas
3. **Diretor** — dashboards de desempenho, notas e faltas da instituição, gestão de usuários, distribuição e monitoramento de créditos

**Tecnologias do motor:** OpenRouter (API unificada multi-modelo) + camada própria de memória persistente e contabilidade de créditos.

---

## 📁 Estrutura do Repositório

```
Meu-Ecoo-Prisma/
│
├── docs/                                      # Documentação do projeto (uma responsabilidade por arquivo)
│   ├── VISAO-DO-PRODUTO.md                    # O que é, para quem, proposta de valor e escopo
│   ├── ARQUITETURA-DO-SISTEMA.md              # Camadas, módulos, fluxo de dados e integração OpenRouter
│   ├── PERFIS-E-PERMISSOES.md                 # Os 3 logins (aluno, professor, diretor) e suas funções
│   ├── CREDITOS-E-ASSINATURAS.md              # Modelo de assinatura, distribuição e contabilidade de créditos
│   ├── MEMORIA-PERSISTENTE.md                 # Como a memória de estudo por aluno é armazenada e usada
│   └── ROADMAP.md                             # Fases de implementação e critérios de pronto
│
├── Documentação/                              # Material de referência do ecossistema (docx/pdf)
│
├── Padrão de qualidade - Felixo System Design/  # Padrões obrigatórios de qualidade (core/ e guias/)
│
├── IA.md                                      # Memória operacional do projeto para sessões de IA
├── README.md
└── LICENSE
```

---

## 📚 Documentação Completa

| Documento | Responsabilidade | O que você encontra |
|-----------|------------------|---------------------|
| **[docs/VISAO-DO-PRODUTO.md](docs/VISAO-DO-PRODUTO.md)** | **Produto** | Problema, público, proposta de valor, escopo do MVP e o que fica de fora |
| **[docs/ARQUITETURA-DO-SISTEMA.md](docs/ARQUITETURA-DO-SISTEMA.md)** | **Arquitetura** | Camadas do sistema, módulos, fluxo de uma requisição de IA e integração com o OpenRouter |
| **[docs/PERFIS-E-PERMISSOES.md](docs/PERFIS-E-PERMISSOES.md)** | **Perfis** | Funções e permissões de aluno, professor e diretor, tela a tela |
| **[docs/CREDITOS-E-ASSINATURAS.md](docs/CREDITOS-E-ASSINATURAS.md)** | **Créditos** | Planos de assinatura, cotas por perfil, contabilidade de tokens e políticas de limite |
| **[docs/MEMORIA-PERSISTENTE.md](docs/MEMORIA-PERSISTENTE.md)** | **Memória** | Modelo de memória por aluno, o que é lembrado, privacidade e ciclo de vida dos dados |
| **[docs/ROADMAP.md](docs/ROADMAP.md)** | **Planejamento** | Fases de implementação, entregáveis e critérios de pronto de cada fase |
| **[IA.md](IA.md)** | **Contexto para IA** | Decisões técnicas, linha do tempo e estado atual para retomada por qualquer sessão de IA |

---

## 👥 Perfis de Acesso

| Perfil | Foco | Principais ferramentas |
|--------|------|------------------------|
| 🧑‍🎓 **Aluno** | Estudar | Tutor de IA com memória, gerador de textos de estudo, simulados, minhas notas e faltas |
| 🧑‍🏫 **Professor** | Ensinar | Geração e correção de provas, banco de conteúdo, material didático, lançamento de notas/faltas |
| 🏛️ **Diretor** | Administrar | Dashboards de desempenho, gestão de usuários e turmas, distribuição e monitoramento de créditos |

Detalhes completos em [docs/PERFIS-E-PERMISSOES.md](docs/PERFIS-E-PERMISSOES.md).

---

## 🛠️ Stack Planejada

Alinhada à stack padrão do **Felixo System Design** (guia de qualidade usado como referência local, não versionado neste repositório):

| Camada | Tecnologia | Papel |
|--------|-----------|-------|
| Frontend | React + TypeScript + Tailwind (Vite) | SPA com áreas separadas por perfil |
| Backend | Django + Django REST Framework | API, regras de negócio, contabilidade de créditos |
| IA | OpenRouter API | Acesso multi-modelo (geração, correção, tutoria) |
| Banco | PostgreSQL | Usuários, conteúdo, notas, faltas, créditos, memória |
| Deploy | Railway | Hospedagem do backend |

---

## 🚧 Status do Projeto

**Fase atual: concepção e documentação.** Ainda não há código de aplicação — este repositório contém a documentação de produto/arquitetura e os padrões de qualidade que guiarão a implementação. Veja o plano em [docs/ROADMAP.md](docs/ROADMAP.md).

---

## 📄 Licença

Este projeto está sob a licença MIT — veja o arquivo [`LICENSE`](LICENSE).

## 👤 Autor

**Projeto ecoVS / Vitis Souls**

---

⭐ Se este projeto te interessou, deixe uma estrela no GitHub!
