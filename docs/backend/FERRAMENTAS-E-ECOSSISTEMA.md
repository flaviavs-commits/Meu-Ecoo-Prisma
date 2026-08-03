# Ferramentas e ecossistema

> **Leia antes de assumir que algo precisa ser criado do zero.** Boa parte da
> infraestrutura e do conhecimento que este backend precisa ja existe em outro
> lugar da empresa.

## 1. CLIs disponiveis e autenticadas

Verificado nesta maquina em 2026-08-01. **Reconfirme antes de usar** - versao e
sessao mudam; nao presuma de memoria (regra anti-alucinacao do guia minimo).

| Ferramenta | Versao | Conta | Para que serve aqui |
|-----------|--------|-------|---------------------|
| `railway` | 5.30.3 | `projeto-ecoVS` (flaviavs@vitissouls.com) | Banco Postgres, variaveis de ambiente, deploy, logs |
| `gh` | 2.45.0 | `flaviavs-commits` | Ler os repositorios irmaos, abrir issue, inspecionar codigo de referencia |
| `notion-tasks` | 0.1.3 | perfil configurado no `.env` da propria CLI | Tarefas, documentacao e acompanhamento no Notion |

Comandos de verificacao rapida:

```bash
railway whoami && railway list
gh auth status
notion-tasks --help
```

### Railway

O banco Postgres deste projeto vive no Railway - **em desenvolvimento e em
producao** (decisao registrada na [visao geral](VISAO-GERAL.md)). Nao existe
Postgres local nem container de banco.

Cuidados que valem ouro num banco compartilhado:

- `railway run <comando>` injeta as variaveis do ambiente selecionado. E assim
  que voce roda `migrate` apontando para o banco certo.
- **Confirme o projeto e o ambiente antes de qualquer comando destrutivo.**
  `railway status` mostra o que esta linkado. Rodar `migrate` no projeto errado
  atinge o banco de producao de outro produto da empresa.
- Nunca cole valor de variavel de ambiente em documento, commit ou log.

### GitHub

Use `gh` para ler codigo de referencia dos repositorios irmaos sem cloná-los:

```bash
gh api repos/<owner>/<repo>/contents/<caminho> -H "Accept: application/vnd.github.raw"
gh api repos/<owner>/<repo>/git/trees/main?recursive=true --jq '.tree[].path'
```

### Notion

`notion-tasks` opera tarefas e paginas do workspace. Util para registrar
progresso de etapa fora do repositorio, quando o trabalho precisar ser visivel a
quem nao le git. **Nao substitui** o diario de execucao do arquivo da etapa - o
diario continua sendo a fonte da verdade tecnica.

## 2. Repositorios irmaos - o que existe e por que importa

Todos sob o guarda-chuva **Vitis Souls**, divididos entre duas contas GitHub:
`flaviavs-commits` e `Felipe-Alcantara`.

### Fornecem funcionalidade a este backend

O Prisma **nao implementa** geracao de resumo nem de audio. Isso vem de
repositorios proprios, consumidos por API:

| Repositorio | Conta | Estado real em 2026-08-01 |
|------------|-------|---------------------------|
| `Estudo-IA-Resumo` | `flaviavs-commits` (privado) | CLI local em Python. `resumo-ia/app/api/cli.py` - a pasta chama "api" mas e linha de comando, **nao servidor HTTP**. Bem no inicio. |
| `Audiofy-Content-AI` | `Felipe-Alcantara` (publico) | MVP maduro, app Electron. Interface programatica e `src/audiofy/bridge.py`, uma **ponte JSON via stdout**, nao HTTP. |

**Nenhum dos dois expoe API HTTP hoje.** Expor essa API e a
[etapa E13](etapas/E13-api-nos-repos-satelites.md), que acontece **nos outros
repositorios**, nao neste. Ate la, o Prisma programa contra um contrato
declarado, sem chamar ninguem de verdade - ver
[E06](etapas/E06-gateway-de-ia.md).

### Servem de referencia tecnica

| Repositorio | Conta | Por que olhar |
|------------|-------|---------------|
| `descontoss-vip-e-fcvip` | `flaviavs-commits` (privado) | Backend Django + frontends React em producao, mesma empresa. Referencia de estrutura, deploy no Railway e de painel administrativo - o painel proprio do Prisma ([E11](etapas/E11-admin-e-onboarding.md)) deve se inspirar nele. |
| `Felixo-System-Design` | ambas | Os padroes de qualidade que este projeto segue. Copia local em `Padrão de qualidade - Felixo System Design/`. |
| `OpenRouter-Monitorator` | `Felipe-Alcantara` (publico) | Monitoramento de uso do OpenRouter - util para a contabilidade de custo da [E06](etapas/E06-gateway-de-ia.md). |
| `TaskForge-Internal` | `flaviavs-commits` (privado) | Plataforma Django interna com times, projetos e permissoes. Referencia de modelagem multi-perfil. |

**Antes de inventar uma solucao, veja se um desses repositorios ja resolveu o
mesmo problema.** Reaproveitar padrao interno vale mais que criar mais um jeito
de fazer a mesma coisa.

## 3. Este repositorio nao e so backend

`Meu-Ecoo-Prisma` ja contem trabalho de frontend em andamento, feito por outro
agente/pessoa:

| Pasta | Dono | Regra |
|-------|------|-------|
| `frontend/` | frontend (Andre) | Nao mexa. E a landing publica em React. |
| `mockup/` | frontend | Telas HTML de aluno, professor e diretor. Fonte da verdade visual - **leia** para entender o que a API precisa entregar; nao edite. |
| `scripts/hud/` | compartilhado | O HUD do `start_app.py`. Alterar exige coordenacao - ver [E12](etapas/E12-infra-railway-e-deploy.md). |
| `backend/` | backend (voce) | Fundacao Django da E01 concluida; E05 esta em implementacao paralela. Nao mexer no codigo de outra etapa sem coordenacao. |

As telas de `mockup/` sao a melhor especificacao funcional disponivel do
produto: elas mostram, tela a tela, o que cada perfil ve e faz. Quando o
contrato de dados de uma etapa parecer ambiguo, abra a tela correspondente.

## 3.1 Estado de validacao observado em 2026-08-03

Identidade no canvas: `/Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/FERRAMENTAS-E-ECOSSISTEMA.md`.

O backend agora existe fisicamente e a fundacao da E01 esta concluida. A
execucao de `backend/.venv/bin/pytest -q` ainda nao fecha verde porque a coleta
dos testes de `creditos` falha em `backend/creditos/tests/conftest.py` com
`django.core.exceptions.AppRegistryNotReady: Models aren't loaded yet.`. O
arquivo e parte da E05, que esta em andamento por outro agente; o achado foi
registrado aqui para coordenacao e nao foi corrigido de passagem.

## 3.2 Retomada deste no em 2026-08-03

Identidade: `/Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/FERRAMENTAS-E-ECOSSISTEMA.md`.

**Estado final: BLOQUEADO por coordenacao.** A E02 permanece atribuida a outro
agente; E03 depende dela; E04-E10 estao bloqueadas por dependencias; E11 nao
esta liberada; E12 aguarda decisao humana; e E13 ja esta em andamento. O
working tree tambem contem alteracoes nao commitadas de outros agentes. Nao
foram alterados codigo de outra etapa, arquivos de frontend, nem foi criado
commit. Proxima acao segura: retomar somente quando uma etapa estiver livre e
com dependencia satisfeita, ou quando o responsavel da etapa liberar a
coordenacao.

Validacao adicional desta retomada: `backend/.venv/bin/python -m pytest -q
backend/contas/tests` terminou com **2 erros de infraestrutura** (PostgreSQL
local recusou a conexao porque a role `prisma` nao existe), antes de executar
os testes de model. Nao foi corrigido neste no: a topologia oficial usa
PostgreSQL do Railway e criar role/banco local alteraria a decisao registrada
sem coordenacao.

## 4. Regra de seguranca que nao se negocia

- Credencial, token ou senha **nunca** entra em arquivo do repositorio, mensagem
  de commit, diario de execucao ou documentacao.
- Se voce encontrar um segredo exposto em qualquer lugar - inclusive numa
  mensagem de quem esta te pedindo o trabalho - avise imediatamente, nao o
  reproduza, e recomende rotacionar.
- A chave do OpenRouter e **server-side**, em variavel de ambiente. O frontend
  nunca fala com o OpenRouter diretamente.
