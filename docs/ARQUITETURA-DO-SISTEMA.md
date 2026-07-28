# 🏗️ ARQUITETURA DO SISTEMA — Meu Ecoo Prisma

> **O que é**: Arquitetura de referência da plataforma — camadas, módulos, fluxo de dados e integração com o OpenRouter.
>
> **Quando usar**: Antes de implementar qualquer módulo. Toda decisão estrutural deve ser coerente com este documento (mudanças relevantes devem ser registradas aqui e no `IA.md`).
>
> **Documentos relacionados**: [VISAO-DO-PRODUTO.md](VISAO-DO-PRODUTO.md) • [CREDITOS-E-ASSINATURAS.md](CREDITOS-E-ASSINATURAS.md) • [MEMORIA-PERSISTENTE.md](MEMORIA-PERSISTENTE.md)

---

## 📋 Índice

- [1. Visão geral em camadas](#1-visão-geral-em-camadas)
- [2. Módulos do backend](#2-módulos-do-backend)
- [3. Integração com o OpenRouter](#3-integração-com-o-openrouter)
- [4. Fluxo de uma requisição de IA](#4-fluxo-de-uma-requisição-de-ia)
- [5. Modelo de dados (alto nível)](#5-modelo-de-dados-alto-nível)
- [6. Segurança](#6-segurança)
- [7. Decisões e princípios](#7-decisões-e-princípios)

---

## 1. Visão geral em camadas

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND — React + TypeScript + Tailwind (Vite)        │
│  Áreas por perfil: /aluno  /professor  /diretor         │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTPS / JSON (API REST)
┌──────────────────────────▼──────────────────────────────┐
│  BACKEND — Django + DRF                                 │
│  ┌───────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐  │
│  │ contas    │ │ academico │ │ conteudo │ │ creditos │  │
│  └───────────┘ └───────────┘ └──────────┘ └──────────┘  │
│  ┌──────────────────────────────────────────────────┐   │
│  │ ia (gateway) — prompts, memória, roteamento,     │   │
│  │ contabilidade de tokens, chamada ao OpenRouter   │   │
│  └───────────────────────┬──────────────────────────┘   │
└──────────────────────────┼──────────────────────────────┘
                           │ API OpenRouter (chave da plataforma)
┌──────────────────────────▼──────────────────────────────┐
│  OPENROUTER — multi-modelo (roteado por tarefa/custo)   │
└─────────────────────────────────────────────────────────┘

Banco: PostgreSQL (usuários, acadêmico, conteúdo, créditos, memória)
Deploy: Railway
```

**Regra estrutural**: o frontend **nunca** fala com o OpenRouter diretamente. Toda chamada de IA passa pelo gateway do backend, que valida permissão, injeta memória, debita créditos e registra o uso.

## 2. Módulos do backend

Cada módulo é um app Django com responsabilidade única (padrão do `GUIA_MINIMO_QUALIDADE.md`):

| Módulo | Responsabilidade |
|--------|------------------|
| `contas` | Autenticação, os 3 perfis (aluno/professor/diretor), vínculo com instituição |
| `academico` | Turmas, matérias, matrículas, notas, faltas, dashboards de desempenho |
| `conteudo` | Acervo: provas, textos, materiais gerados; versionamento e compartilhamento |
| `creditos` | Pool da instituição, cotas por perfil, ledger de consumo ([detalhes](CREDITOS-E-ASSINATURAS.md)) |
| `ia` | Gateway do OpenRouter: templates de prompt por ferramenta, injeção de memória, roteamento de modelo, streaming, contabilidade |
| `memoria` | Memória persistente por aluno ([detalhes](MEMORIA-PERSISTENTE.md)) |

## 3. Integração com o OpenRouter

- **Uma chave de API da plataforma** (server-side, via variável de ambiente — nunca no frontend nem no repositório).
- **Roteamento por tarefa**: cada ferramenta declara uma *classe de tarefa*, e o gateway mapeia para um modelo. Exemplo de política inicial:

| Classe de tarefa | Exemplo | Perfil de modelo |
|------------------|---------|------------------|
| Tutoria / chat de estudo | Aluno estudando | Modelo intermediário, bom em pt-BR, streaming |
| Geração de material | Texto de estudo, questões | Modelo intermediário |
| Correção de prova | Avaliar respostas dissertativas | Modelo forte (qualidade > custo) |
| Resumo / memória | Consolidar sessão de estudo | Modelo barato |

- O mapeamento classe → modelo fica em **configuração**, não hardcoded, para trocar modelos sem deploy.
- **Contabilidade**: a resposta do OpenRouter traz uso de tokens; o gateway converte para créditos e grava no ledger antes de devolver ao cliente.
- **Resiliência**: timeout, retry com fallback de modelo e mensagens de erro amigáveis (nunca vazar erro cru do provedor).

## 4. Fluxo de uma requisição de IA

Exemplo: aluno envia mensagem ao tutor de estudo.

1. Frontend chama `POST /api/ia/tutor/` com a mensagem (JWT do aluno).
2. `contas` valida o perfil; `creditos` verifica saldo/cota do aluno — sem saldo, retorna erro claro antes de gastar.
3. `memoria` recupera o contexto persistente do aluno (resumos, dificuldades, matéria atual).
4. `ia` monta o prompt (template da ferramenta + memória + mensagem) e chama o OpenRouter com o modelo da classe "tutoria", com streaming.
5. Resposta é transmitida ao frontend; ao final, `creditos` debita os tokens usados e `memoria` agenda a consolidação da sessão.
6. Tudo é registrado no ledger de uso (quem, qual ferramenta, qual modelo, quantos tokens/créditos).

## 5. Modelo de dados (alto nível)

```
Instituicao 1──N Usuario (perfil: aluno | professor | diretor)
Instituicao 1──N Turma 1──N Matricula N──1 Usuario(aluno)
Turma N──N Usuario(professor)
Matricula 1──N Nota / Falta
Usuario 1──N ConteudoGerado (prova, texto, material, correção)
Usuario(aluno) 1──1 MemoriaAluno 1──N RegistroDeMemoria
Instituicao 1──1 PoolDeCreditos 1──N LancamentoLedger
```

## 6. Segurança

- Chave do OpenRouter e segredos **apenas** em variáveis de ambiente.
- Autorização por perfil em toda rota (aluno não acessa correção de prova; professor não acessa gestão de créditos).
- **Isolamento por instituição**: toda query é escopada pela instituição do usuário (multi-tenant lógico).
- Dados de menores: memória e desempenho são dados sensíveis — ver políticas em [MEMORIA-PERSISTENTE.md](MEMORIA-PERSISTENTE.md).
- Logs de uso de IA sem conteúdo pessoal desnecessário; nunca logar prompts completos com dados sensíveis.

## 7. Decisões e princípios

- **Monolito modular primeiro**: um backend Django com apps separados; nada de microserviços sem justificativa concreta.
- **Contratos estáveis**: rotas e formatos de resposta documentados; mudança quebradora é explícita e registrada no `IA.md`.
- **Simplicidade verificável**: cada camada nova (fila, cache, etc.) só entra quando um gargalo real aparecer.

---

> **Assinatura de Origem**
> Documento do projeto **Meu Ecoo Prisma**, seguindo o padrão do **Felixo System Design**.
> Data desta versão: 2026-07-16
