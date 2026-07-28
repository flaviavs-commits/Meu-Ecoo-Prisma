# 🧠 MEMÓRIA PERSISTENTE — Meu Ecoo Prisma

> **O que é**: Especificação da memória de estudo por aluno — o que a IA lembra entre sessões, como isso é armazenado, usado e protegido.
>
> **Quando usar**: Ao implementar o módulo `memoria` e o tutor de estudo.
>
> **Documentos relacionados**: [ARQUITETURA-DO-SISTEMA.md](ARQUITETURA-DO-SISTEMA.md) • [PERFIS-E-PERMISSOES.md](PERFIS-E-PERMISSOES.md)

---

## 📋 Índice

- [1. Objetivo](#1-objetivo)
- [2. O que é lembrado](#2-o-que-é-lembrado)
- [3. Como funciona](#3-como-funciona)
- [4. Estrutura de armazenamento](#4-estrutura-de-armazenamento)
- [5. Privacidade e controle](#5-privacidade-e-controle)
- [6. Ciclo de vida](#6-ciclo-de-vida)

---

## 1. Objetivo

Transformar o chat de IA em um **tutor contínuo**: cada sessão de estudo parte do que o aluno já estudou, das dificuldades identificadas e do progresso registrado — em vez de começar do zero como um chat genérico.

## 2. O que é lembrado

| Categoria | Exemplos |
|-----------|----------|
| **Perfil de estudo** | Série/turma, matérias, estilo de explicação que funciona melhor |
| **Progresso por matéria** | Tópicos estudados, nível de domínio percebido |
| **Dificuldades** | Conceitos com erro recorrente (ex.: "confunde razão e proporção") |
| **Histórico de sessões** | Resumo curto de cada sessão de estudo |
| **Metas** | Prova na próxima semana, tópico a revisar |

**O que NÃO é memorizado**: conversa literal completa (apenas resumos), dados pessoais irrelevantes ao estudo, e qualquer conteúdo sensível fora do contexto pedagógico.

## 3. Como funciona

Ciclo por sessão de estudo:

1. **Recuperação** — ao abrir o tutor, o gateway de IA carrega a memória do aluno: perfil de estudo + resumos recentes + dificuldades da matéria em foco.
2. **Injeção** — essa memória entra no prompt como contexto estruturado e estável (favorecendo cache de prompt).
3. **Sessão** — o aluno estuda normalmente; a conversa corrente vive só na sessão.
4. **Consolidação** — ao encerrar (ou por inatividade), um modelo barato gera o **resumo da sessão**: o que foi estudado, avanços, dificuldades novas. Esse resumo é gravado; a conversa crua é descartada após a janela de retenção.
5. **Atualização de domínio** — dificuldades e progresso por tópico são atualizados a partir do resumo e dos resultados de simulados.

A consolidação usa a classe de tarefa "resumo/memória" ([roteamento](ARQUITETURA-DO-SISTEMA.md#3-integração-com-o-openrouter)) — custo mínimo de créditos.

## 4. Estrutura de armazenamento

```
MemoriaAluno (1 por aluno)
├── perfil_de_estudo        # preferências e contexto estáveis (JSON estruturado)
├── dominio_por_topico      # matéria → tópico → nível + evidências
└── RegistroDeMemoria (N)   # entradas datadas, imutáveis
    ├── tipo: resumo_sessao | dificuldade | meta | marco
    ├── conteudo (texto curto)
    └── origem: tutor | simulado | professor
```

- Registros são **imutáveis e datados** (linha do tempo, mesmo princípio do `IA.md` do Felixo): correções entram como novo registro, não como edição.
- Armazenamento em PostgreSQL; busca por matéria/tópico/recência. Busca semântica (embeddings) só se a recuperação simples se mostrar insuficiente — simplicidade verificável primeiro.

## 5. Privacidade e controle

- A memória é **do aluno**: outro aluno nunca a acessa.
- **Professor** vê apenas indicadores agregados derivados (ex.: tópicos com dificuldade na turma), não a memória individual crua.
- **Diretor** vê apenas métricas de uso, nunca conteúdo de memória.
- O aluno pode **ver e apagar** entradas da própria memória (transparência).
- Dados de menores de idade: tratados como sensíveis (LGPD) — minimização, sem uso fora da finalidade pedagógica, sem envio ao OpenRouter além do necessário para a sessão.

## 6. Ciclo de vida

| Evento | Efeito |
|--------|--------|
| Fim do período letivo | Memória é compactada (resumo do ano por matéria) |
| Aluno muda de turma/série | Perfil atualizado; histórico preservado |
| Aluno desativado | Memória congelada; expurgo após prazo de retenção da instituição |
| Instituição encerra contrato | Exportação e exclusão conforme contrato/LGPD |

---

> **Assinatura de Origem**
> Documento do projeto **Meu Ecoo Prisma**, seguindo o padrão do **Felixo System Design**.
> Data desta versão: 2026-07-16
