# IA.md - Contexto Operacional

[2026-08-03] **Projeto Railway do Prisma identificado** por /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/CONSTITUICAO-MODULARIDADE.md: `Meu-Ecoo-Prisma`, ambiente `production`, com Postgres e API online. A URL disponível para o serviço Postgres é privada (`postgres.railway.internal`) e não resolve na máquina local; `DATABASE_PUBLIC_URL` não está configurada. A E02 segue bloqueada para validação remota até existir uma URL pública/encaminhamento autorizado ou execução de comandos no ambiente Railway. Validação local estrutural com SQLite temporário: 5 testes passaram; `manage.py check` ainda acusa referências da E05 a apps `ia` e `academico` ainda não instalados.

[2026-08-03] **Decoração da tela de escolha removida por Codex gpt-5.6-luna yolo  Estudo-com-IA**: retiradas as linhas diagonais, gradientes, pontilhado, losango e prisma decorativo de `mockup/index.html`; permanecem o logo, a divisão dos painéis e os elementos funcionais de escolha. Validação: screenshot Playwright em 390x844 e 1920x1080, sem overflow horizontal.

[2026-08-03] **Retomada do canvas por `/Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/README.md`**: não havia etapa de backend livre para assumir com segurança; E02 está atribuída, E05/E08/E13 têm trabalho paralelo e as demais dependem de etapas bloqueadas. Validação do estado atual: `cd backend && .venv/bin/pytest -q` falhou na coleta em 3 arquivos de testes da E05 porque `creditos.models` não está associado a um app em `INSTALLED_APPS` (`RuntimeError: Model class creditos.models.Lancamento ... isn't in an application in INSTALLED_APPS`). Correção deve ser feita pelo responsável da E05, sem sobrescrever os arquivos não versionados dele. Estado desta retomada: **bloqueado por trabalho paralelo/dependências; próxima ação concreta é o agente E05 registrar o app `creditos` e repetir os testes**.

[2026-08-03] **Integração mínima da E05 registrada por `/Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/README.md`**: `creditos` foi adicionado a `INSTALLED_APPS` em `backend/config/settings/base.py`, sem alterar a implementação do agente E05. Após a correção, a coleta passou e a suíte chegou a `3 passed, 14 errors`; os erros restantes são conexão ao PostgreSQL local (`FATAL: role "prisma" does not exist`), coerente com a decisão do projeto de usar PostgreSQL do Railway e com a ausência de banco local. Estado: **bloqueado por infraestrutura de banco; código de registro do app validado até a etapa de conexão**.

[2026-08-03] **Mobile-first concluído por Codex gpt-5.6-luna yolo  Estudo-com-IA**: landing React e telas HTML de entrada, login, aluno, professor e diretor receberam ajustes de responsividade, áreas de toque, CTAs fluidos, contenção de overflow, tabelas móveis e compressão do Tutor em telefones estreitos. Validação concluída: `npm run lint`, `npm run build`, varredura UTF-8 em 54 arquivos e Playwright nas 6 rotas visuais em 390x844, sem overflow horizontal nem erros de console; landing também verificada em 1280x800. Estado desta rodada: **concluído**. Limite conhecido: backend e autenticação continuam fora do código existente e não foram implementados nesta rodada.

[2026-08-03] Segunda passada visual na tela de escolha: ambientação geométrica sutil, prisma ampliado no painel escuro, indicador das três rotas, copy reduzida, cards com microinterações e responsividade mobile refinada. Validação: cópia sincronizada no PrismaTest e lint/build do frontend passaram.

[2026-08-03] Tela de escolha de perfil refinada em `mockup/index.html`: divisão entre identidade e entrada agora é exatamente 50/50; cards de aluno, professor e diretor ficaram mais compactos, numerados e tecnológicos, com estados de foco/hover acessíveis. A tela continua sendo a fonte de verdade sincronizada pelo PrismaTest.

[2026-08-03] **E01 (fundacao do projeto Django) concluida** por Claude, agente identificado no canvas como `docs/backend/contratos/API-CONVENCOES.md`. Primeira linha de codigo do backend: `backend/` com Django 5.2 + DRF, settings por ambiente (`config/settings/base.py`/`dev.py`/`prod.py`), `GET /api/v1/health/`, exception handler unico no formato do contrato (`core/erros.py`), `pytest` com 3 testes passando via TDD e `pip-audit` sem vulnerabilidades. Commit `92c915c`. Duas decisoes de projeto (nao so de etapa) que valem registrar aqui:
  - **Nao existe projeto "Prisma" no Railway ainda** (`railway list` mostrou 13 projetos da empresa, nenhum com esse nome). Isso bloqueia a validacao real de `DATABASE_URL` contra o Postgres do Railway - a E01 rodou so contra um `.env` local nunca conectado de fato. Escopo de destravar isso e da **E12**; ate la, qualquer etapa que precise de banco real fica com essa mesma limitacao.
  - **Python 3.12 nao esta instalado nesta maquina** (so 3.11.15 e 3.14.3 via Homebrew) - o venv do backend usa 3.11 por decisao pratica, registrada tambem no diario da E01. Se 3.12 for instalado depois, recriar `backend/.venv`.
  - **Contradicao de desenho corrigida**: a E01 original mandava deixar o app `contas` vazio com `AUTH_USER_MODEL = "contas.Usuario"` ja apontado - isso quebra o Django de verdade (`django.contrib.auth` resolve o model em `AppConfig.ready()`, nao so na migracao). A correcao foi criar um stub minimo (`class Usuario(AbstractUser): pass`) em `contas/models.py`. Consequencia para quem pegar a **E02**: o model ja existe como classe Python, o trabalho e editar/estender, nao criar do zero.
  - Confirmado ao vivo que o ambiente multi-agente esta em uso real: `backend/creditos/` (E05) e trabalho paralelo de outro agente ja estavam la quando a E01 comecou a escrever codigo.

## Estado atual (resumo vivo)

<!--
  EXCECAO a regra append-only desta secao: ela e um RESUMO reescrevivel.
  Responde "onde o projeto esta AGORA" em poucas linhas, para retomar contexto
  sem reler toda a linha do tempo abaixo. Reescreva-a a cada mudanca de estado.
-->

[2026-08-03] Landing page concluida em `frontend/` (React 19 + TypeScript + Vite 8 + Tailwind 4 + Motion 12); telas por perfil em `mockup/`. **O MVP backend local esta implementado**: E01, E03-E11 entregues em Django/DRF, com SQLite para desenvolvimento e TDD; E02 permanece bloqueada somente quanto a validacao remota de multi-tenancy. A integracao inicial esta em `/entrar`: e-mail e senha, access token apenas em memoria, refresh em cookie HttpOnly e CORS local. O HUD agora prepara SQLite, sobe Django e Vite em sequencia e encerra as arvores de processos em Windows/macOS/Linux. Railway fica fora do ciclo local enquanto a assinatura estiver pendente. Ponto de entrada: [`docs/backend/README.md`](docs/backend/README.md).

## Objetivo do projeto

[2026-07-28] Implementacao web do produto concebido em `Estudo-com-IA`: plataforma SaaS de estudos para instituicoes de ensino usando **OpenRouter como motor de IA**. A instituicao assina, recebe creditos de IA, e o diretor distribui para professores (gerar/corrigir provas e material) e alunos (tutor com memoria persistente). Tres perfis de login: aluno, professor, diretor.

O repositorio `Estudo-com-IA` mantem a documentacao de concepcao (visao, arquitetura, perfis, creditos, memoria, roadmap) e um mockup HTML estatico. Este repositorio contem o codigo real.

- [2026-07-31] **Uso exclusivo institucional (B2B escola), reafirmado pelo Andre: "nao e mais para usuarios soltos".** Historico completo: em 2026-07-16 o produto nasceu como SaaS institucional; em 2026-07-17 (registrado so na memoria externa da IA, nunca neste arquivo) houve um pivo temporario para centro de estudos individual/solo, sem escola por tras; em algum ponto antes de 2026-07-28 o projeto voltou para o modelo institucional (e e o que este arquivo documenta desde entao - ver linha 15 e [[projeto-onboarding-escola-manual]]). O pedido de hoje confirma esse modelo institucional como definitivo e aponta um resíduo esquecido da era individual: `mockup/login.html` ainda oferecia autocadastro (`Ainda nao tem conta? Criar conta` -> `criar-conta.html`), contradizendo o onboarding manual (Andre configura a conta da escola apos fechar contrato) que a landing real (`frontend/`) ja seguia desde o commit `da904ba` ("CTA final aponta para contato, nao para cadastro automatico"). Correcao: removido `mockup/criar-conta.html` e a tela `criar-conta.html` da lista `TELAS` de `scripts/sincronizar-app.py`; o rodape de `login.html` virou "Sua escola ainda nao usa o Prisma? Fale com a gente" (href placeholder `#`, mesmo padrao da landing real, ate existir e-mail de contato definido). Sincronizado para `frontend/public/app/` (15 arquivos, um a menos que antes por causa da remocao). Se aparecer nova mencao a cadastro individual/self-service em qualquer tela, e residuo da mesma era e deve ser removida do mesmo jeito.

## Estado atual

- **Implementado**: landing, login em `/entrar`, cliente API, contexto de sessao, backend Django/DRF das etapas E01 e E03-E11, SQLite local, e HUD modular em `scripts/hud/` para subir os dois servidores.
- **Validado**: backend com `pytest`, frontend com Vitest/lint/build, CORS e login real contra `127.0.0.1:8000`.
- **Pendente**: protecao das telas estaticas de `/app/`, integracao das telas por perfil com a identidade autenticada, validacao remota final da E02 e a decisao de infraestrutura E12/E13.

## Stack e dependencias

- Frontend: React 19 + TypeScript + Vite 8 + Tailwind 4 (instalado, em `frontend/`)
- Playwright (devDependency, `frontend/`): instalado em 2026-07-29 para permitir screenshot real da landing renderizada. Sem ele, mudancas visuais (logo, layout) so eram validadas por lint/build/inspecao de codigo - nunca por olhar a pagina de fato. Chromium baixado localmente via `npx playwright install chromium`.
- Backend: Django 5.2.16 + DRF 3.17.1 (monolito modular), em `backend/`. Fundacao (E01) concluida em 2026-08-03. Python 3.11.15 (3.12 pedido pelo desenho, indisponivel nesta maquina - ver diario da E01).
- Banco: PostgreSQL (Railway) - projeto "Prisma" ainda nao existe la, entao nenhuma conexao real foi validada ainda
- IA: OpenRouter (API unificada multi-modelo)
- Deploy: Railway
- Testes: `pytest` + `pytest-django` no backend e Vitest no frontend, com TDD nos fluxos de autenticacao e contrato API (ver `backend/` e `frontend/src/api/`)

## Decisoes de arquitetura

Herdadas da concepcao em `Estudo-com-IA/IA.md` e ainda validas:

- [2026-07-16] **OpenRouter como provedor unico de IA** - API unificada multi-modelo permite roteamento por classe de tarefa (tutoria, geracao, correcao, resumo) otimizando custo dos creditos. Mapeamento classe-modelo em configuracao, nao em codigo.
- [2026-07-16] **Credito como unidade interna** - conversao custo-do-modelo para creditos por tabela configuravel com margem; saldo derivado do ledger (fonte unica), debito so apos resposta bem-sucedida.
- [2026-07-16] **Memoria por resumos consolidados, nao conversa crua** - sessoes sao resumidas por modelo barato em registros imutaveis datados; recuperacao simples (materia/topico/recencia) antes de considerar embeddings.
- [2026-07-16] **Monolito modular primeiro** - sem microservicos/fila/cache ate gargalo real (principio "simplicidade verificavel" do `GUIA_MINIMO_QUALIDADE.md`).
- [2026-07-16] **Conteudo de IA nasce rascunho** - prova/nota so vale apos revisao explicita do professor (decisao pedagogica e de responsabilidade).
- [2026-07-16] **Gateway de IA no backend** - toda chamada de IA passa pelo backend; o frontend nunca fala com o OpenRouter diretamente.

Apps Django planejados: `contas`, `academico`, `conteudo`, `creditos`, `ia`, `memoria`.

- [2026-08-01] **System design do backend fechado e escrito em `docs/backend/`**, a partir de um questionario de alinhamento respondido pela Flavia. Entregue como 13 etapas independentes (`docs/backend/etapas/E01..E13`), 4 contratos compartilhados (`contratos/`) e um protocolo de trabalho, de forma que **um agente diferente possa tocar cada etapa** sem depender de um so. Cada arquivo de etapa tem um "Diario de execucao" que o agente responsavel preenche **enquanto** trabalha - se a sessao cair, o proximo retoma dali. Decisoes travadas nesta rodada, com o motivo:
  - **Multi-tenancy por coluna `instituicao_id`**, nao schema nem banco por escola. Schema-por-tenant (`django-tenants`) foi considerado e recusado: o isolamento extra nao paga a complexidade de migracao e operacao na escala de partida (um cliente grande, ~5 mil alunos). Mitigacao do risco de vazamento: base abstrata + manager com escopo explicito + teste estrutural que falha se um model novo esquecer o escopo, e recurso de outra instituicao respondendo **404, nao 403** (403 confirmaria a existencia do id).
  - **Postgres do Railway em dev e em producao.** Sem SQLite local, sem container de banco - a topologia de dev passa a ser igual a de producao. Custo aceito: depende de rede e da conta Railway para desenvolver.
  - **Creditos: termina a tarefa em andamento, depois bloqueia a proxima.** O gate e `saldo > 0`, nao `saldo >= custo`, entao o saldo pode negativar pelo custo de uma unica chamada. Escolhido para nunca cortar uma resposta do tutor pela metade. **Isso e comportamento correto, nao bug.**
  - **JWT (simplejwt)** com rotacao de refresh e blacklist, Argon2 e rate limit no login. Pendencia deliberada: onde a SPA guarda o token (cookie `httpOnly` vs `localStorage`) muda o trabalho do frontend e ficou para decisao conjunta.
  - **Conversa bruta do tutor E persistida**, ao lado de uma memoria consolidada compactavel. Isto **refina** o registro de 2026-07-16 ("memoria por resumos consolidados, nao conversa crua"): hoje os dois coexistem. Prazo de retencao do bruto continua **pendencia aberta** - nada deve ser apagado ate haver decisao.
  - **Upload em disco** (Volume do Railway), atras de adaptador de storage para migrar a nuvem por configuracao quando/se a API escalar horizontalmente.
  - **Django Admin nesta fase**, com painel proprio adiado para etapa futura.
  - **Ha menores de idade na base** (o produto atende fundamental e medio, nao so universidade). Isso virou contrato proprio: `docs/backend/contratos/LGPD-E-DADOS-SENSIVEIS.md`. Consequencia mais forte: professor e diretor **nao** leem a conversa crua do aluno.
- [2026-08-01] **Resumos e geracao de audio nao serao implementados aqui**: vem de `Estudo-IA-Resumo` (flaviavs-commits) e `Audiofy-Content-AI` (Felipe-Alcantara), consumidos por API. **Achado que muda o plano**: inspecionados via `gh`, nenhum dos dois expoe API HTTP hoje - `Audiofy` tem uma ponte JSON por stdout (`bridge.py`, usada pelo app Electron) e `Estudo-IA-Resumo` tem uma CLI (`app/api/cli.py`, a pasta chama "api" mas e linha de comando). Expor essas APIs virou a etapa E13, que acontece **naqueles repositorios**, nao neste, e nao bloqueia a fundacao: o Prisma programa contra o contrato declarado, com um provedor falso no lugar do real.
- [2026-08-01] **Residuo do modelo antigo ainda vivo na landing**: `frontend/src/content/landing.ts` anuncia tres planos individuais pagos (Prisma / Pro / Ultra, R$ 39,99 a R$ 99,99, "sem contrato, sem fidelidade"). E da era em que o produto era vendido direto ao aluno - mesma familia dos achados de `criar-conta.html` (2026-07-31) e "Workspaces" no `professor.html`. **O backend nao modela plano individual.** A limpeza da landing e trabalho do frontend; registrado aqui para nao se perder.

## Decisoes de design e convencoes

- [2026-07-28] Padroes de qualidade sincronizados em `doktor SystemDesign/` via comando global `doktor`. A pasta e uma copia sincronizada, nao editavel neste projeto: mudancas de padrao vao no repositorio Doktor System-Design.
- [2026-07-28] Commits seguem Conventional Commits: `tipo(escopo): descricao no imperativo`.
- [2026-07-28] **Marca do produto: "Prisma"**. A metafora e a refracao - um tema entra, materiais de estudo saem em tres direcoes (aluno, professor, diretor). O logo e um prisma com feixe de entrada e espectro de saida nas tres cores de perfil.
- [2026-07-28] **Tailwind 4 com plugin `@tailwindcss/vite`**, nao PostCSS. A v4 dispensa `tailwind.config.js`: tokens ficam em `@theme` dentro de `frontend/src/index.css`. Versao confirmada na instalacao (4.3.3), nao presumida - v3 e v4 configuram de formas incompativeis.
- [2026-07-28] **Copy separada do JSX** em `frontend/src/content/landing.ts`. Editar texto da landing nao exige mexer em componente.
- [2026-07-28] **Um tom por perfil** (`--color-aluno`, `--color-professor`, `--color-diretor`) em vez de uma unica familia de cor, conforme `DESIGN_SYSTEM_FRONTEND.md` secao 4.
- [2026-07-28] **Depoimentos ficam como placeholder** ate a instituicao coletar relatos reais. Publicar depoimento ficticio como se fosse real e falso testemunho de cliente; os cards usam borda tracejada para deixar o estado pendente visivel.

- [2026-07-28] **Divisao de trabalho por camada**: Andre no frontend, Felipe no backend. Ao propor trabalho de backend (models, autenticacao, gateway de IA), declarar o contrato e o ponto de integracao em vez de implementar direto.
- [2026-07-28] **Paleta e tipografia passam a ser normativas**, conforme o documento de identidade UX/UI recebido: `#F7F5EE`, `#1A1A1A`, `#C85A3C`, `#6A8550`, `#7B78C8`; Josefin Sans em caixa alta com tracking `0.08em` nos titulos, Inter no corpo. Substitui os tons dessaturados que eu havia proposto antes - agora ha fonte de verdade escrita.
- [2026-07-28] **Contorno em grafite suavizado, nao `#1A1A1A` puro.** Desvio consciente do documento: preto solido em tela cheia pesa demais. A borda continua nitida e sem sombra difusa, que e o que define o estilo. Tokens `--color-contorno` e `--color-contorno-forte`.

- [2026-07-28] **Secoes em `min-h-svh`.** Secoes curtas deixavam a cor da secao seguinte vazar para o campo de visao. `svh` e nao `vh` porque a barra do navegador em celular provoca salto com `vh` fixo.
- [2026-07-28] **Motion (ex-Framer Motion) como biblioteca de animacao.** Custo real: bundle de 214 kB para ~354 kB (66 -> 112 kB comprimido). Aceito para landing; se performance virar prioridade, `motion/react-m` com carregamento sob demanda reduz.
- [2026-07-28] **Sem Lottie e sem three.js.** Ambos foram avaliados: sem alguem produzindo arquivos no After Effects, seriam dependencia morta no bundle. O prisma refratando e as letras 3D sao SVG e CSS. Se surgir producao de `.lottie`, `@lottiefiles/dotlottie-react` e o caminho.
- [2026-07-29] **Constituicao de modularidade: cada arquivo com UMA responsabilidade.** Regra estrutural obrigatoria e permanente redigida pelo Andre, com prioridade sobre preferencia pessoal de organizacao. Texto completo em [`docs/CONSTITUICAO-MODULARIDADE.md`](docs/CONSTITUICAO-MODULARIDADE.md); resumo operacional na secao 4 do `AGENTS.md`. O motivo e custo de manutencao: consertar um detalhe num arquivo de 1700 linhas obriga a IA a ler 1700 linhas - tempo, token e risco de efeito colateral. Proibe arquivos deposito (`utils`, `helpers`, `misc`, `common`); exige um componente/hook/contexto/tipo por arquivo; define limites por tipo (componente 120/200, hook 80/150, Python 150/300, conteudo e CSS 150/250, documento 250/400) como alerta estrutural, com quebra por responsabilidade e nao por contagem de linha. Debitos registrados: `start_app.py` (1716) e `IA.md` (351, append-only).
- [2026-07-29] **`start_app.py` quebrado no pacote `scripts/hud/`.** Primeira aplicacao da constituicao de modularidade. O arquivo tinha 1716 linhas e seis responsabilidades (decodificar terminal, desenhar, checar ambiente, cinco widgets, montar janela, executar acoes); so a classe `Hud` ocupava 818 linhas com mais de 50 metodos. Virou um gatilho de 48 linhas que faz `from scripts.hud import abrir`. O comportamento e o mesmo - o HUD continua sendo janela Tkinter, com o desvio de 2026-07-29 intacto. Modulos: `caminhos`, `tokens`, `desenho`, `processos`, `ambiente`, `fontes`, `layout`, `status`, `console`, `acoes`, `janela`, mais `widgets/` com um arquivo por widget. `Hud` compoe quatro mixins (`LayoutMixin`, `StatusMixin`, `ConsoleMixin`, `AcoesMixin`). Maior modulo: `layout.py`, 280 linhas, dentro do limite de 300. Ganho pratico: mudar a cor de um card passou de ler 1716 linhas para ler 178 (`widgets/card_acao.py`).
- [2026-07-29] **Constituicao mora em `docs/`, nao no `AGENTS.md`.** O texto completo tem ~250 linhas e o `AGENTS.md` e lido a cada sessao: embuti-lo cobraria esse custo de contexto em toda tarefa, contradizendo o proprio principio que a regra defende. O `AGENTS.md` fica com resumo denso (limites, proibicoes, criterio de quebra) e ponteiro; a versao integral e consultada em refatoracao e revisao estrutural.
- [2026-08-03] **Registros de trabalho concluido de 2026-07-29 e 2026-07-31 movidos, sem edicao, para [`docs/ia-archive/IA-ARCHIVE-2026.md`](docs/ia-archive/IA-ARCHIVE-2026.md)** - o arquivo tinha passado de 400 linhas, o teto da constituicao de modularidade. O criterio nao foi puramente cronologico: sairam os **relatos retrospectivos** (refacao visual do aluno, favicon, tema em professor/diretor, bugs de `animarNumero` e de FOUC, retrabalho do Tutor), que descrevem trabalho ja entregue e nao regem decisao nenhuma daqui pra frente. Ficaram aqui, independente da data, as **decisoes e convencoes ainda em vigor** - marca, Tailwind 4, copy fora do JSX, tom por perfil, constituicao de modularidade, HUD Tkinter, pivo B2B. Quem precisar do detalhe de execucao de uma dessas entregas (medicao WCAG, causa raiz de um bug, o que foi verificado com Playwright) le o arquivo; quem so precisa saber como o projeto decide, le aqui.
- [2026-08-03] **`professor.html` e `diretor.html` traduzidas nos 5 idiomas** - fecha a pendencia aberta em 2026-07-29 e repetida em 2026-07-31 ("sem `data-i18n` porque professor/diretor ainda nao tem i18n"). Ate aqui so o aluno trocava de idioma: um diretor ou professor abrindo a demo em ingles via a topbar sem o seletor e a tela inteira em portugues. Nada de motor novo - `assets/i18n.js` ja servia as tres telas, faltava marcar o HTML e escrever as chaves. O que foi feito em cada uma: symbol `#i-globe` (nao existia nesses dois arquivos), o dropdown `dd-lang` na topbar na mesma posicao do aluno (antes do toggle de tema), `<script src="assets/i18n.js">` antes do `app.js`, e os atributos `data-i18n`/`data-i18n-html`/`data-i18n-attr` no conteudo (180 no professor, 236 no diretor). Dicionarios foram de 171 para **453 chaves por idioma**.
  - **O que nao foi traduzido, de proposito**, seguindo a convencao ja registrada no cabecalho do `i18n.js`: nomes de pessoas, titulos dos materiais do acervo, nomes das turmas (`Português ENEM`) e o enunciado das questoes geradas na previa. Sao o roteiro da demo, nao interface - e um material de escola brasileira continua sendo brasileiro numa demo em alemao.
  - Numeros ficaram **fora** da chave sempre que possivel: `<td>7,0 <span data-i18n="prof.sugerido">sugerido</span></td>` em vez de uma chave "7,0 sugerido". Evita ter 6 chaves quase iguais so porque a nota muda, e o dia que esses numeros vierem da API o texto ao redor ja esta separado.
  - Chaves compartilhadas entre perfis foram reusadas (`conta.*`, `topbar.*`, `materia.*`, `acao.fechar`), mas **`Desempenho` do diretor ganhou chave propria** (`dir.desempenho`) depois que o teste mostrou o menu em alemao dizendo "Fortschritt" (de `progresso.eyebrow`, do aluno) e o h1 da mesma tela dizendo "Leistung". Reuso de chave por texto igual em portugues quebra quando as linguas divergem.
  - Serie escolar virou chave (`serie.ano6`...`serie.em3`) em vez de texto solto - alem de traduzir (`9º ano` -> `9th grade` / `Klasse 9` / `3e`), deixa o vocabulario K-12 num lugar so, caso a decisao pendente de adaptar a demo para ensino superior seja tomada.
  - Novo script `scripts/verificar-i18n.py`: confere que todo `data-i18n` usado no HTML existe e que os 5 dicionarios tem exatamente o mesmo conjunto de chaves. Existe porque esse erro e silencioso - chave errada nao quebra nada, o portugues do HTML fica como fallback e a tela so parece "nao traduzida naquele pedaco". Saida atual: `ok - 453 chaves em 5 idiomas`, com aviso de 2 chaves sem uso no HTML (`materiais.contagemSingular`, `tutor.mensagem`) que sao aplicadas por JS em `app.js`, nao no markup.
  - **Verificado via Playwright** (nao so o script de chaves): nas duas telas, os 5 idiomas trocam de fato o `h1` de **todas** as secoes do menu e o `document.documentElement.lang`, o modal "Minha conta" abre traduzido, zero erros de console. Amostra em alemao - professor: `Start | Klassen | Inhalte | Korrektur | Materialbestand | KI-Analysen`; diretor: `Überblick | Leistung | Anwesenheit | KI-Credits | Berichte | Kollegium`.
  - **Ressalva mantida de 2026-07-29**: ES/FR/DE feitos com cuidado terminologico, sem revisao de falante nativo. Agora com um agravante proprio destas telas - termos de sistema escolar (serie, bimestre, mantenedora, conselho de classe) nao tem equivalente exato e foram aproximados para o sistema de cada pais. Revisao recomendada antes de usar numa apresentacao nessas linguas.
  - Sincronizado para `frontend/public/app/` via `scripts/sincronizar-app.py` (18 arquivos).
- [2026-08-03] **`index.html` e `login.html` traduzidas, fechando o i18n do mockup inteiro.** Eram justamente as duas **primeiras** telas da demo e as ultimas em portugues: dava para trocar para alemao dentro do app, sair, e cair num login em portugues - com a preferencia salva no `localStorage` funcionando, so que sem nada traduzido para aplicar nela.
  - **Seletor proprio, nao o da topbar.** Estas duas telas nao usam `ui.css` nem `app.js` (tem CSS inline e layout `.split` proprio), entao nao havia topbar onde encaixar o dropdown existente. Solucao: uma `.langbar` fixa no canto superior direito, um grupo de cinco botoes `PT EN ES FR DE` reaproveitando a classe `.lang-opt` - o `marcarSelecionado()` do `i18n.js` ja destaca o ativo sem codigo novo. A ligacao com o motor sao tres linhas de `addEventListener`. Precisa existir aqui e nao so no app porque quem abre o login direto nao teria **nenhum** outro lugar para escolher a lingua.
  - **Textos que o JS escrevia foram tirados do JS.** O copyright montava a frase inteira em JavaScript (`'© ' + ano + ' Prisma. Todos os direitos...'`), o que a deixava fora do alcance do i18n por construcao; agora o HTML tem a frase com `data-i18n` e o script so escreve o ano num `<span id="ano">`. O rotulo de perfil (`Entrando como aluno`) e o `aria-label` do olho de senha (`Mostrar`/`Ocultar`) passaram a trocar de **chave** em vez de texto, com `PrismaI18n.aplicarEm()` - mesmo padrao que o `app.js` ja usava para o contador de materiais.
  - `verificar-i18n.py` passou a **ler tambem os `.js`**: as chaves aplicadas em tempo de execucao apareciam como "sem uso no HTML" e o aviso de chave orfa nascia com falso positivo. Um aviso que erra e um aviso que ninguem le. Com o JS incluido sobrou uma orfa real, `tutor.mensagem`, sem uso em lugar nenhum desde a refacao do Tutor - removida dos 5 dicionarios. Total: **482 chaves por idioma**, mockup 100% traduzido.
  - **Verificado via Playwright**: os 5 idiomas trocam texto e `documentElement.lang` no index; navegar index -> login **preserva** o idioma escolhido (o caso que motivou o trabalho); o `<title>`, o `placeholder` do e-mail e o `aria-label` do toggle de senha traduzem; ida e volta para pt-BR restaura tudo; "Entrar" leva ao perfil certo. Zero erros de console. Screenshots em 1440x900 e 390x844 confirmam que a `.langbar` nao colide com o conteudo (no mobile ela cai sobre a coluna escura, e a pilula creme mantem contraste).
  - **Risco que corri e que fica de licao**: durante o trabalho rodei `git checkout -- mockup/index.html mockup/login.html` para desfazer uma edicao minha duplicada. Havia outro agente trabalhando no mesmo repositorio nesta janela. Deu certo por sorte de cronologia - o trabalho dele nesses arquivos ja estava commitado em `dd96928`. Conferido depois pelo diff (toda linha removida era uma que eu proprio substitui), mas o certo era ter conferido **antes**: `git checkout --` num repositorio multi-agente descarta trabalho nao commitado de quem quer que seja, sem aviso e sem recuperacao. Mesma familia do incidente de `rm` registrado em 2026-07-31.
- [2026-08-03] **Coluna de escolha de perfil de `index.html` enxugada** (pedido do Andre sobre um screenshot: "tem muita informacao aqui vei... minimalista, bem estruturado"). O problema nao era layout, era **repeticao**: a etiqueta "01 / ESCOLHA O PERFIL", o titulo "Como voce quer entrar?", o subtitulo "Escolha seu espaco no Prisma" e a fileira de bolinhas "ALUNO PROFESSOR DIRETOR" diziam a mesma coisa **quatro vezes**, e a fileira listava exatamente os mesmos tres nomes dos cards logo abaixo. Dentro de cada card havia mais tres marcadores redundantes da mesma acao: o numero (01/02/03), o sufixo "/ ENTRAR" e a seta.
  - **Removidos**: etiqueta de secao, subtitulo, fileira de bolinhas, numeracao dos cards e o sufixo "/ entrar". Sobrou um titulo curto (`Entrar como`) e tres linhas. Com so tres opcoes, cada elemento a mais e uma coisa para ler ANTES de poder clicar - e essa tela existe para ser atravessada, nao lida.
  - **Descricoes cortadas pela metade**: "tutor com memoria, simulados e o proprio boletim" -> "tutor, simulados e boletim"; "gestao de creditos, turmas e desempenho da instituicao" -> "creditos, turmas e desempenho". Mesma informacao, uma batida de olho em vez de uma leitura.
  - **Cor saiu do bloco e foi para a borda.** Os cards tinham corpo inteiro preenchido de lavanda/salmao/verde, o que fazia o olho ir ao retangulo colorido antes de ir ao nome. Agora o corpo usa o creme da pagina, a cor fica num filete de 3px na lateral e no icone, e o preenchimento tonal so aparece no hover - onde ele de fato informa alguma coisa (qual linha esta sob o cursor).
  - Quatro chaves de i18n sairam dos 5 dicionarios com os elementos que as usavam (`entrada.comoEntrar`, `entrada.escolhaPerfil`, `entrada.escolhaEspaco`, `entrada.tresCaminhos`) e entrou `entrada.entrarComo`. Total: **479 chaves por idioma**. O `verificar-i18n.py` confirma que nenhuma chave ficou orfa nem faltando.
  - **Verificado via Playwright**: screenshots em 1440x900 e 390x844 sem overflow horizontal e sem erro de console, os cards traduzem (alemao: "Anmelden als" / "Lernende:r - Tutor, Probeexamen und Zeugnis"), e clicar num card continua levando para `login.html?perfil=<perfil>`.

### [2026-07-31] Limpeza sem querer de arquivos de outro agente

Ao remover meus proprios scripts `qa-*.mjs` descartaveis em `frontend/`, tambem apaguei `frontend/qa-tutor.mjs`, `frontend/qa-tutor/` e `frontend/qa-zoom.mjs` - nao eram meus, provavelmente scripts de verificacao de outro agente trabalhando em paralelo na mesma sessao (relacionados aos CSS `tutor.css`/`tutor-painel.css` do item de 2026-07-29 acima). Eram arquivos nao versionados (`??` no git), sem como recuperar. **Licao para qualquer IA lendo isto**: antes de rodar `rm` numa pasta compartilhada como `frontend/` neste repositorio multi-agente, confirme que cada arquivo listado foi criado por voce mesma na sessao atual - nao presuma que "parece um script de teste descartavel" significa que e seu.

### [2026-07-29] start_app.py e um HUD grafico, nao um menu de terminal

CONTEXTO: o `GUIA-START-APP-SCRIPT.md` do Doktor exige um menu interativo
**no terminal** (`questionary` + `rich`), rodando em Windows, Linux e macOS.

DECISAO (Andre): trocar o menu de terminal por uma janela Tkinter - status do
ambiente ao vivo e acoes em botoes. Tkinter porque ja vem com o Python: zero
dependencia nova, e o projeto nao tinha nenhuma dependencia Python ate aqui.

POR QUE: o publico roda isso numa maquina com display, e a landing e um produto
visual - a porta de entrada acompanha.

CUSTO ACEITO, e o ponto importante: **nao ha mais porta de entrada em ambiente
sem display** (SSH, container, CI). O script detecta a ausencia de display e
imprime os comandos equivalentes (`npm install`, `npm run dev`, `npm run lint
&& npm run build`), mas isso e uma saida de emergencia, nao um menu. Quem
precisar operar o projeto remotamente usa npm direto.

Isto e um desvio consciente do guia, registrado aqui porque o guia e normativo:
quem for auditar o projeto contra o Doktor vai encontrar a divergencia e o
motivo. Se a decisao for revertida, o menu de terminal esta no historico do git
(commit anterior a esta mudanca), ja corrigido e testado.

### [2026-07-28] Landing e aplicacao: dois repositorios, uma copia derivada

CONTEXTO: a landing (aqui) e a vitrine; a aplicacao - telas de aluno, professor e diretor - vive em `Estudo-com-IA`, pasta `mockup/`. O "Entrar" precisa abrir a aplicacao.
ALTERNATIVAS: (a) publicar os mockups e linkar por URL externa; (b) copiar para `public/` e servir junto; (c) reescrever as telas em React.
DECISAO: (b). Os mockups sao autossuficientes (sem CDN, assets relativos), entao servir de `frontend/public/app/` funciona sem reescrever caminho. `Estudo-com-IA` continua sendo a fonte da verdade; `scripts/sincronizar-app.py` traz a versao atual. A pasta esta no `.gitignore`: e derivada, versiona-la criaria duas copias divergindo.
CONSEQUENCIA: quando as telas mudarem no outro repositorio, e preciso rodar o script de novo. Registrado no README.
DETALHE: as telas linkam para `landing.html`, que nao e copiada. O script reescreve esse link para a raiz - sem isso da 404 em servidor estatico (em dev o Vite disfarca, devolvendo o fallback do SPA).
VALIDACAO: `curl` em `/`, `/app/index.html`, as tres telas de perfil e os assets - todos 200.

### [2026-07-28] A landing nao pergunta o perfil: a aplicacao ja pergunta

CONTEXTO: eu havia criado uma secao de escolha de perfil na landing, antes de saber que a aplicacao tem a propria tela inicial ("Como voce quer comecar?").
DECISAO: remover a secao da landing. Duas telas seguidas com a mesma pergunta seria atrito sem ganho. O "Entrar" (header, menu mobile e CTA final) aponta para `ENTRADA_APP`, que e a tela inicial da aplicacao.
NOTA: `EscolhaPerfil.tsx`, `AreaPerfil.tsx`, `areas.ts` e `useRota.ts` foram criados e removidos na mesma sessao - eram contorno para um bloqueio que nao existia (os mockups estavam acessiveis localmente o tempo todo).

### [2026-07-28] ACESSIBILIDADE: acento colorido nao serve para texto pequeno

CONTEXTO: o documento de identidade alerta para lavanda em texto pequeno. Medi o contraste dos tres acentos contra os fundos reais da pagina.
MEDICAO: terracota 3.21-4.15:1 | oliva 3.15-4.06:1 | lavanda 2.98-3.85:1. **Nenhum** atinge os 4.5:1 que a WCAG AA exige para texto pequeno - o problema e mais amplo do que o documento sugere. Lavanda sobre tint terracota (2.98) reprova ate para texto grande.
DECISAO: acento vive em marcador, faixa, filete, icone decorativo e borda. Texto legivel usa grafite ou `texto-secundario` (5.48-6.78:1). Registrado como regra 5 no topo de `index.css`, com a tabela.
VALIDACAO: script de contraste executado sobre os pares reais de cor; rotulos de perfil no demo migrados de acento para `texto-secundario`.

### [2026-07-28] Desempenho: a primeira versao das animacoes travava

CONTEXTO: com titulo letra a letra, atmosfera de quatro camadas e cards 3D, a pagina engasgava ao rolar.
CAUSAS: (a) cada letra desenhada 4x com `mix-blend-screen` - 160 nos de composicao num titulo de 40 letras; (b) `radial-gradient` remontado a cada quadro via `useMotionTemplate`, forcando repintura; (c) `mask-image` e `filter: blur` animados por scroll, das operacoes mais caras do CSS.
DECISAO: refracao por `text-shadow` (um no por letra); brilho especular por `transform` sobre gradiente fixo; portal so com `opacity` e `scale`; atmosfera de quatro camadas para duas, sem o grao em `mix-blend-overlay`.
VALIDACAO: build e lint limpos. **Pendente**: medicao real de FPS em navegador - nao foi possivel nesta sessao.

### [2026-07-28] Landing page: React desde o inicio, sem etapa em HTML puro

CONTEXTO: pedido de clonar uma landing page de referencia (Prism Labs, produto de terceiro). O repositorio ainda nao tinha frontend.
ALTERNATIVAS: (a) HTML unico com Tailwind por CDN, migrando para React depois; (b) ja scaffoldar React + Vite + Tailwind.
DECISAO: (b). O `AGENTS.md` ja fixa React + TS + Vite + Tailwind como stack; comecar em HTML criaria retrabalho de migracao.
DECISAO DE CONTEUDO: estrutura e padroes de UI foram usados como referencia, mas marca, copy e depoimentos da pagina original nao foram copiados - o texto foi escrito a partir do proprio `IA.md` (3 perfis, OpenRouter, creditos, memoria persistente).
VALIDACAO: `npm run build` compilou (tsc + vite, 31 modulos, 0 erro); `npm run lint` (oxlint) sem apontamentos; dev server respondeu HTTP 200 com o `<title>` correto; copy das 7 secoes e tokens de cor conferidos no bundle de producao; `start_app.py` executado (status, opcao invalida e saida).

## Testes importantes

[2026-08-03] A landing continua visual, mas a entrada autenticada agora tem regra de negocio e contrato API. Por isso o frontend ganhou Vitest para o cliente HTTP; o backend continua com `pytest`/`pytest-django` e TDD. A validacao manual do HUD permanece necessaria porque Tkinter depende de display.

Validacao da integracao frontend/backend em 2026-08-03:

| Verificacao | Comando | Resultado |
|-------------|---------|-----------|
| Cliente API | `cd frontend && npm test` | 2 testes passaram: payload de e-mail/senha, cookie de refresh e erro padronizado |
| Frontend estatico | `npm run lint` e `npm run build` | ambos passaram; TypeScript e bundle Vite sem erro |
| Backend completo | `cd backend && .venv/bin/pytest -q` | 101 passaram, 1 ignorado |
| Configuracao Django | `.venv/bin/python manage.py check` e `makemigrations --check --dry-run` | sem problemas e sem migracoes pendentes |
| Dependencias frontend | `npm audit --audit-level=high` | 0 vulnerabilidades encontradas |
| Health local | `curl http://127.0.0.1:8000/api/v1/health/` | HTTP 200, `{"status":"ok"}` |
| Login/CORS local | `curl` com Origin `http://127.0.0.1:5174` e cookie | login retornou access token, cookie HttpOnly e `Access-Control-Allow-Credentials: true` |

Validacao estrutural do HUD apos a integracao:

| Verificacao | Comando | Resultado |
|-------------|---------|-----------|
| Sintaxe e importacao | `python3 -m compileall -q scripts/hud start_app.py` | OK |
| Portas POSIX | script local contra `lsof` | listeners encontrados; frontend 5174 identificado |
| Arvore de processos | inspecao de `SAIDA_SUBPROCESSO` e `encerrar_arvore` | nova sessao no macOS/Linux e encerramento por grupo; `taskkill /T` preservado no Windows |
| Fluxo principal | leitura dirigida de `acao_servidor` e `BackendMixin` | migrate SQLite conclui antes do Vite; falha do backend nao inicia frontend |

Verificacao da quebra do `start_app.py` em 2026-07-29 (saida observada,
nao presumida):

| Verificacao | Comando | Resultado |
|-------------|---------|-----------|
| Pacote importa e mixins resolvem | `python -c "from scripts.hud import Hud"` | OK; MRO `Hud -> LayoutMixin -> StatusMixin -> ConsoleMixin -> AcoesMixin`; nenhum metodo faltando |
| Janela monta de fato | `Hud(tk.Tk())` + `raiz.update()` | 8 cards, 5 linhas de status, 16 fontes; `_pintar_status` e `_escrever` sem erro |
| Modal abre, avisa e cancela | `Modal(...)` + `_cancelar()` | abriu com entrada, `resultado` volta `None` |
| Comandos internos do console | `_comando_interno('help')`, `('pwd')` | ambos OK |
| Porta de entrada real | `python start_app.py` | janela abriu, saida 0 |
| Sintaxe de todos os modulos | `python -m compileall scripts/ start_app.py` | OK |
| Referencia orfa ao arquivo antigo | `grep "from start_app\|import start_app"` | nenhuma |

Verificacao manual executada em 2026-07-28:

| Verificacao | Comando | Resultado |
|-------------|---------|-----------|
| Compilacao TS + bundle | `npm run build` | 31 modulos, 0 erro, ~228ms |
| Lint | `npm run lint` (oxlint) | sem apontamentos |
| Servidor de dev | `npm run dev` + `curl` | HTTP 200, `<title>` correto |
| Copy das 7 secoes | grep no bundle de producao | todas presentes |
| Tokens de cor | grep no CSS de producao | presentes (ver observacao abaixo) |
| Menu de entrada | `python start_app.py` | status, opcao invalida e saida ok |

Observacao: `--color-erro` nao aparece no CSS compilado porque o Tailwind 4 so emite token efetivamente usado, e a landing nao tem estado de erro. O token segue definido em `index.css` e sera emitido quando um formulario usar. Nao e defeito.

Pendente de verificacao manual: renderizacao em navegador real (mobile e desktop) e navegacao por teclado ponta a ponta. O HTML foi construido com foco visivel, `aria-label` no menu, `aria-pressed` nas abas do demo e skip link, mas isso ainda nao foi conferido com leitor de tela.

[2026-08-03] **Integracao local por /Users/thonychesse/Documents/GitHub/Meu-Ecoo-Prisma/docs/backend/etapas/E01-fundacao-do-projeto.md:** conectei `/entrar` ao backend Django usando somente e-mail e senha. O cliente separa transporte (`frontend/src/api/cliente.ts`), sessao (`frontend/src/auth/`) e UI (`frontend/src/components/auth/PaginaLogin.tsx`); nao usa `localStorage` nem expoe segredo. O HUD foi ajustado em `scripts/hud/` para preparar SQLite, iniciar backend e frontend em sequencia, reconhecer listeners no macOS/Linux e encerrar grupos de processos sem deixar Vite/Django orfaos. Validacao: tabela acima, backend 101 passed/1 skipped, frontend 2 testes, lint/build/check/migracoes e login/CORS reais.

[2026-07-28, segunda rodada] Apos identidade visual, animacoes e reestruturacao:

| Verificacao | Comando | Resultado |
|-------------|---------|-----------|
| Compilacao TS + bundle | `npm run build` | 439 modulos, 0 erro |
| Lint | `npm run lint` (oxlint) | sem apontamentos |
| Contraste WCAG dos acentos | script sobre os pares reais de cor | ver registro datado acima |
| Paleta e fontes no CSS de producao | grep no bundle | 8 hex e 2 familias presentes |
| Acentuacao no bundle | grep + varredura de mojibake | integra, sem corrupcao |
| HUD abre e pinta | `python start_app.py` + captura de tela | janela renderiza, 4 linhas de status em verde |
| HUD: acao Validar | clique real no botao + captura | `oxlint` correu em thread, saida no painel, "Lint aprovado" em verde |
| HUD: acao Sincronizar | clique real no botao + captura | 7 arquivos, "Telas sincronizadas." em verde |
| HUD: porta ocupada | clique em "Rodar o site" com 5173 em uso | recusou com mensagem acionavel, sem travar |
| HUD: dialogo de porta | clique em "Configurar porta" | dialogo abre pre-preenchido com a porta atual |
| HUD sem display | `tk.Tk` forcado a levantar `TclError` | imprime os comandos npm e sai com codigo 1 |
| HUD: ciclo subir/parar | script dirigindo `Hud` real (`acao_rodar`/`acao_parar`) | sobe, status vira "rodando", para, status volta a "livre" |
| HUD: sem processo orfao | `Get-NetTCPConnection` + `Win32_Process` apos parar | porta livre, nenhum `node` do PrismaTest sobrevivente |
| HUD: saida sem ANSI | log lido apos `npm run dev` | "➜ Local: http://localhost:5173/" limpo, sem escapes |
| Console: executa comandos | `npm run lint`, `git status`, `echo` digitados | rodaram e imprimiram a saida real |
| Console: acento do shell | comando inexistente (mensagem do cmd) | "operável" correto, sem mojibake |
| Console: codigo de saida | `cmd /c exit 3` | "[saiu com codigo 3]", com sinal |
| Console: cd e pwd | `cd ..`, `pwd`, `cd frontend`, pasta invalida | navega, rotulo acompanha, erro claro |
| Console: historico | seta cima/baixo apos varios comandos | percorre e volta a linha vazia |
| Console: Ctrl+C | `ping -n 20` interrompido | arvore encerrada, processo morto |
| Barra de rolagem | 600 linhas, topo/meio/fim | polegar 24px em todas as posicoes, dentro do trilho |
| Modal: aparencia | screenshot real, janela + modal juntos | cantos arredondados, paleta e tipografia do HUD |
| Modal: validacao de porta | 5 rodadas seguidas (valida, invalida, texto, cancelar, valida) | cada rodada com foco e resultado corretos |
| Modal: fechar com servidor ativo | "manter aberto" simulado | janela sobrevive, servidor continua marcado |
| Modal: centralizacao | 3 aberturas seguidas | sempre fora do canto (0,0), posicao estavel |
| Logo: coordenadas | conversao do SVG original (1254x1254) vs. pontos usados no React/HUD | topo, esq, dir, base, meio - todos a menos de 0.05px |
| Logo: HUD | captura de tela do cabecalho | triangulo com aresta central e "V" da base, no lugar do quadrado "P" |
| Logo: favicon | `curl` no `/favicon.svg` servido pelo Vite | path identico ao aplicado, `<link rel="icon">` aponta certo |
| Logo: landing (header e rodape) | Playwright real, screenshot do `<header>` e do `<footer>` | logo em terracota no header, em grafite no rodape, "PRISMA" inalterado |

Nao verificado nesta sessao: FPS das animacoes, comportamento em telas pequenas e leitor de tela do site - depende de olhar humano no navegador. No HUD, o unico caminho nao exercitado e "Instalar dependencias" com `node_modules` ausente, que exigiria apagar a pasta; os demais foram testados por clique real ou por script dirigindo a classe `Hud`.

## Bugs e fixes relevantes

- **[2026-07-29] Acentos quebrados na saida do `start_app.py`.** O console do
  Windows abre em `cp1252` e o arquivo e UTF-8: "instituicoes" saia como
  `institui??es`. O arquivo sempre esteve correto - quem quebrava era a saida.
  Corrigido na origem com `sys.stdout.reconfigure(encoding="utf-8")`, sem tirar
  acento do texto. Mesma preocupacao do commit `7f0da4f`, uma camada abaixo.
  (O HUD grafico que veio depois nao tem esse problema, mas a causa vale
  registro: qualquer script Python deste projeto que imprima acento no Windows
  precisa do mesmo cuidado.)

- **[2026-07-29] Logo oficial adotada em landing, favicon e HUD.** O André
  trouxe `prisma-logo-minimal.svg` (triângulo com aresta central e "V" da
  base) como ícone definitivo do projeto. Antes disso o favicon era um SVG
  roxo/azul solto em `frontend/public/`, sem relação com a paleta creme
  atual - provavelmente sobra de uma fase anterior da identidade.

  Aplicado nos três lugares a partir do mesmo conjunto de coordenadas
  (viewBox original 1254x1254, convertido para 32x32):
    - `frontend/src/components/ui/Logo.tsx` - o componente React que o
      Header e o Rodapé já usavam, então a landing herda sem mudar
      chamada nenhuma.
    - `frontend/public/favicon.svg` - substituído pelo mesmo path.
    - `start_app.py`, `desenhar_logo_prisma()` - o Tk não importa SVG,
      então os 3 traços são redesenhados com `create_line` nas mesmas
      coordenadas. Validado numericamente: os pontos usados no HUD batem
      com a conversão do SVG original (topo, esq, dir, base, meio - todos
      a menos de 0.05px de diferença).

  Ajustes finos feitos depois, todos a pedido do André e verificados com
  captura real via Playwright (não só lint/build):
    - **Cor**: terracota tentado primeiro (mesma regra de `text-marca` da
      landing), depois revertido para grafite (`#1a1a1a`/`text-texto`) em
      tudo - decisão final do André.
    - **Tamanho do ícone**: 20px→30px na landing, 30px→42px no HUD.
    - **ViewBox recortado**: de `0 0 32 32` para `5.15 5.18 21.8 21.39`
      (os limites reais do desenho, com margem simétrica de 1.2). O
      viewBox original tinha folga maior embaixo que em cima, o que fazia
      o triângulo "flutuar" acima da linha de base do texto.
    - **Alinhamento vertical**: tentei compensar com `-translate-y-1` no
      ícone pra bater com a base óptica das letras (medida via
      `Canvas.measureText`) - ficou pior, com o ícone flutuando pra cima.
      Revertido para `items-center` puro (sem deslocamento extra), que o
      André confirmou como mais equilibrado.
    - **Tamanho do texto**: `text-lg` (18px) → `text-xl` (20px) em
      `LogoComNome`, pra reequilibrar a proporção com o ícone maior -
      confirmado pelo André como a versão final ("assim maior ficou
      melhor"). O Rodapé herda automaticamente por usar o mesmo
      componente; não precisou editar `Rodape.tsx`.

  Lição: medição de pixel (bounding box, centro geométrico, base óptica)
  nem sempre prediz o que o olho julga alinhado - o ajuste "matematicamente
  correto" do deslocamento vertical ficou pior na prática. Testar
  visualmente com captura real, não só a métrica, é o que decide.

  Motivo do redesenho em vez de embutir o SVG cru no HUD: Tkinter não tem
  parser de SVG. A alternativa seria uma dependência de imagem (Pillow +
  rasterizar o SVG), que o guia mínimo de qualidade não justificaria para
  um ícone de 30px.

- **[2026-07-29] Diálogos do sistema (simpledialog/messagebox) destoavam do HUD.**
  A janela de "Configurar porta" e a de confirmação ao fechar saíam com a
  aparência crua do Windows - cinza, fonte do sistema, sem nenhuma relação
  com a identidade do Prisma. Substituídas por `Modal`, uma janela própria
  (Canvas com cantos arredondados, mesma paleta e tipografia dos cards).
  Dois bugs surgiram ao construir e só apareceram testando de verdade:

  1. **Foco perdido na segunda abertura.** `focus_set()` só agenda o foco;
     se o SO ainda segurava o foco em outro widget (ex.: o console, após um
     modal anterior fechar), o pedido não tinha efeito e Enter/Esc paravam
     de responder. Reproduzido abrindo o modal de porta duas vezes seguidas
     - a segunda vinha com `focus_get() is None`. Corrigido com
     `focus_force()`.
  2. **Modal nascia em (0,0), no canto da tela, por uma corrida.** Com
     `overrideredirect(True)` (sem decoração), o Windows só reflete a
     posição real depois de um ciclo do laço principal -
     `update_idletasks()` não bastava. `_centralizar()` agora chama
     `update()` ao final.

  Ambos confirmados com um teste programático que abre o modal 5 vezes
  seguidas e verifica foco e posição a cada rodada.

- **[2026-07-29] Console do HUD virou terminal, e o codepage quebrava acento.**
  As mensagens do proprio `cmd.exe` saem no codepage OEM (cp437/cp850 aqui),
  nao em UTF-8: decodificar tudo como UTF-8 transformava "operável" em
  "oper?vel". As ferramentas do projeto (npm, git, node) escrevem UTF-8, entao
  a leitura tenta UTF-8 e cai no OEM detectado em runtime (`GetOEMCP`) quando a
  linha nao e UTF-8 valido. Ver `decodificar()`.

- **[2026-07-29] Codigo de saida aparecia sem sinal.** `npm` falhando com -4058
  era mostrado como `4294963238`. No Windows o valor vem como unsigned de 32
  bits; agora e convertido antes de exibir.

- **[2026-07-29] Console espremido a 4 linhas.** Duas causas somadas: a area de
  saida era empacotada antes da linha de comando e ficava com `expand=True`,
  deixando a entrada com 1px; e a coluna pedia 1213px numa janela de 1020, com
  o grid tirando a diferenca da unica linha elastica (a do console). Corrigido
  empacotando a entrada primeiro, movendo a coluna de `pack` para `grid` com
  peso so na linha do console, e dimensionando a janela pelo `reqheight` real
  (`_ajustar_altura`). Cards passaram de 78px para 66px para liberar altura.
  Resultado medido: console de 61px (4 linhas) para 239px (14 linhas).

- **[2026-07-29] `tk.Scrollbar` nao aceita estilo no Windows.** Saia sempre com
  o bloco cinza do widget de sistema, com setas. Substituida por `BarraRolagem`,
  um Canvas com polegar arredondado que some quando nao ha o que rolar e respeita
  um minimo de 24px (senao vira um risco impossivel de pegar com o mouse).

- **[2026-07-29] "Parar servidor" deixava o Vite vivo.** `npm run dev` e um
  wrapper: quem abre a porta e um `node` neto. `Popen.terminate()` matava so o
  wrapper e o neto ficava orfao segurando a 5173 - o HUD dizia "parado" com o
  site no ar. Confirmado por `Win32_Process`: o `node` sobrevivente tinha como
  pai um pid que ja nao existia. Corrigido com `encerrar_arvore()`, que usa
  `taskkill /F /T` no Windows (arvore inteira) e `terminate()` fora dele.

- **[2026-07-29] Status parava de atualizar em silencio.** A medicao de porta
  foi para uma thread (para nao travar a janela), mas a thread chamava
  `raiz.after()` - o Tkinter so aceita chamada da thread principal e levantava
  `RuntimeError: main thread is not in main loop`. Como a excecao morria dentro
  da thread daemon, nada aparecia: o painel simplesmente congelava. A thread
  agora so publica na fila; quem repinta e o `_drenar_fila`, ja na thread da
  interface. Achado ao dirigir o HUD por script, nao pelo uso normal.

- **[2026-07-29] Codigos ANSI apareciam crus no painel de saida.** O Vite
  colore a saida; no widget de texto do Tk isso vira `<-[32m` visivel. Removidos
  na entrada do log (`limpar_ansi`), ja que o painel tem cor propria por tag.

- **[2026-07-29] Checagem de porta dava falso negativo.** Testar so
  `127.0.0.1` dizia "porta livre" com o Vite rodando e respondendo HTTP 200:
  o Vite escuta em `::1` (IPv6), confirmado com `Get-NetTCPConnection`
  (`LocalAddress ::1`). `porta_em_uso()` testa as duas familias. Sem isso o
  status do HUD mentiria - e o guia exige que status cheque de verdade.

## Integracoes e servicos externos

- Servico: **OpenRouter** (planejada)
- Como esta configurado: ainda nao configurado
- Onde ficam variaveis: variavel de ambiente server-side, fora do repositorio
- Observacao de seguranca: chave unica da plataforma, nunca no frontend nem versionada

## Pendencias

- [ ] Definir se `Estudo-com-IA` continua como repositorio de concepcao ou se a documentacao migra para ca.
- [x] ~~Fase 0: frontend React com `start_app.py`~~ - landing entregue em 2026-07-28.
- [x] ~~Ligar a landing as telas da aplicacao~~ - feito em 2026-07-28 via `scripts/sincronizar-app.py`.
- [x] Fase 0: backend Django + login por e-mail e senha entregue localmente em `/api/v1/auth/`; o frontend usa `/entrar`, recebe a identidade e mantem o access token somente em memoria.
- [x] Sessao inicial integrada: refresh em cookie HttpOnly, logout com blacklist e CORS com credenciais para Vite local. Falta conectar a identidade as telas estaticas de `/app/`.
- [ ] Conferir FPS real das animacoes em navegador, sobretudo em maquina modesta.
- [ ] Fase 1: gateway OpenRouter + modulo de creditos + primeira ferramenta de IA.
- [x] Definir estrategia de testes e comando de validacao objetiva: Vitest no cliente API, `pytest` no backend, mais lint/build.
- [ ] Substituir os depoimentos placeholder por relatos reais coletados na instituicao.
- [ ] Ligar os CTAs (`#comecar`, `#entrar`) as telas reais quando a autenticacao existir.
- [ ] Ligar o demo do motor de refracao ao gateway de IA (hoje e estatico e ilustrativo).
- [ ] Preencher as paginas legais do rodape (privacidade, termos, seguranca). Como a plataforma trata dados de alunos, ha dever de LGPD - ver `templates/PRIVACIDADE-LGPD-template.md` no Doktor.
- [ ] Conferir a landing em navegador real (mobile/desktop) e navegacao por teclado.
- [ ] **Arquivar os registros antigos deste `IA.md`.** Em 2026-08-01 o arquivo passou de 400 linhas, o limite da constituicao de modularidade. Mover os registros mais antigos, **sem editar**, para `docs/ia-archive/IA-ARCHIVE-2026.md`, deixando um ponteiro datado aqui. E mudanca estrutural: merece commit proprio, e nao deve ser feita "de passagem" numa tarefa que nao a envolve.
- [ ] Remover os tres planos individuais (Prisma / Pro / Ultra) de `frontend/src/content/landing.ts` - residuo do modelo pre-institucional, ver registro de 2026-08-01. Trabalho de frontend.
- [x] Decidir onde a SPA guarda o token JWT: access token somente em memoria; refresh em cookie `HttpOnly`, com CORS por credenciais no desenvolvimento local. Validado por testes do backend e do cliente API.
- [ ] Definir o prazo de retencao da conversa bruta do tutor - pendencia de LGPD, ver `docs/backend/etapas/E07-memoria-e-conversas.md`. Ate la, nao apagar nada.

## Resumos de decisao

Use quando houver decisao complexa:

```text
[YYYY-MM-DD] CONTEXTO:
ALTERNATIVAS:
DECISAO:
VALIDACAO:
```

Nao registre chain of thought interno. Registre apenas informacao tecnica util, verificavel e retomavel.

Nao apague nem reescreva registros antigos ao mudar uma decisao: adicione um novo registro datado explicando a mudanca, o motivo e a validacao. A unica secao reescrevivel e "Estado atual (resumo vivo)".

Quando este arquivo crescer demais, mova os registros mais antigos (sem editar) para `docs/ia-archive/IA-ARCHIVE-<ano>.md` e deixe um ponteiro datado aqui.
