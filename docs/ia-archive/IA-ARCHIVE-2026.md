# IA-ARCHIVE-2026.md - Registros arquivados de 2026

> Registros de trabalho concluido movidos de `IA.md` em 2026-08-03, quando
> aquele arquivo passou de 400 linhas (teto da constituicao de modularidade).
>
> **Copiados sem edicao.** Sao relatos retrospectivos: descrevem o que foi
> feito, como foi verificado e por que, em entregas ja concluidas. As decisoes
> e convencoes que ainda regem o projeto ficaram no `IA.md` - nao procure
> aqui como o projeto decide hoje, procure o que aconteceu naquele dia.
>
> Este arquivo e append-only como o `IA.md`: nada aqui se reescreve.

## Registros de 2026-07-29 e 2026-07-31

- [2026-07-29] **`aluno.html` refeita no padrao Prisma: dark mode + i18n (5 idiomas) + correcao de bugs**, servindo de molde para `professor.html`/`diretor.html` (ainda nao migradas). Mudancas em `Estudo-com-IA/mockup/`:
  - **Paleta**: tokens de `assets/ui.css` trocados de verde/dourado generico para creme/grafite/lavanda oficial do Prisma. Acento do aluno = lavanda (`--green:#7b78c8`), mas texto pequeno usa `--green-ink:#5b58a8` (mais escuro) por causa de contraste - ver WCAG abaixo. Nomes de variavel antigos (`--green`) mantidos para nao reescrever todo o CSS consumidor; so o valor semantico mudou. `.btn-pri` corrigido para usar `--ink` (grafite) em vez da cor de perfil, seguindo a regra do design system de que acento de perfil nao e CTA universal.
  - **Dark mode**: implementado via `@media (prefers-color-scheme:dark)` + `:root[data-theme="dark"]`/`:root[data-theme="light"]` explicitos, com persistencia em `localStorage` (`prisma-theme`). Fundo genuinamente escuro (`#151412`, nao cinza medio disfarcado), decisao confirmada com o Andre. Toggle na topbar (`#themebtn`, icone sol/lua) e o toggle "Modo escuro" do modal de conta (que antes era decorativo, sem JS/CSS ligado) agora sao o mesmo estado sincronizado.
  - **i18n**: motor vanilla proprio em `assets/i18n.js` (`data-i18n`/`data-i18n-html`/`data-i18n-attr`, sem framework), 5 idiomas (PT-BR/EN/ES/FR/DE) em `assets/i18n/*.json`, 169 chaves cada, validadas identicas entre arquivos. Seletor de idioma na topbar ao lado do toggle de tema. Persistencia em `localStorage` (`prisma-lang`). **Ressalva**: traducoes feitas com cuidado terminologico mas sem revisao de falante nativo em ES/FR/DE - recomendada antes de producao.
  - **Bugs corrigidos**: toggles `.tg` genericos eram puramente decorativos (sem `role="switch"`/`aria-checked`/persistencia) - corrigido com o mesmo padrao ja usado corretamente pelo toggle do modo Tutor. Cores hardcoded (verde `rgba(14,138,87,...)`, gradiente do `.card.hero`) que quebrariam no dark mode - migradas para tokens/`color-mix`. Chave i18n duplicada com dois textos-fonte diferentes (`tutor.focoDificuldades` servindo dois sentidos) - separada em `simulados.focarDificuldades`.
  - **Correcao de marca em todas as telas do mockup** (interrupcao do usuario durante a etapa acima, fora do escopo original de so `aluno.html`): sidebar ainda mostrava "Estudo IA" com icone generico (`#i-spark`) em vez do triangulo Prisma real. Corrigido em `aluno.html`, `professor.html`, `diretor.html`, `index.html`, `landing.html` - todas agora usam o symbol SVG `#i-logo` (mesmo path do `Logo.tsx`) e o nome "Prisma". De passagem, corrigido bug pre-existente em `professor.html` que dizia "· Tutor" em vez de "· Professor" no titulo da aba.
  - **Contraste WCAG medido** (luminancia relativa) para os pares finais: lavanda pura `#7b78c8` sobre creme `#f7f5ee` = 3.59:1 (reprova texto pequeno, por isso `--green-ink` existe); lavanda escura `#5b58a8` sobre creme = 5.65:1 (passa); grafite `#1a1a1a` sobre creme = 15.95:1; lavanda pura sobre fundo escuro `#151412` = 4.70:1 (passa); texto claro `#f0ece1` sobre fundo escuro = 15.60:1. Confirmado por leitura do CSS que os usos de `--green` puro sao so decorativos (fundo de icone, borda, sombra) e o texto de fato usa `--green-ink`.
  - **Verificado via Playwright** (nao assumido): toggle de tema muda `data-theme`, persiste apos reload, icone sol/lua troca corretamente, toggle do modal sincroniza; os 5 idiomas trocam o `h1` e `document.documentElement.lang` corretamente; idioma persiste apos reload; toggle `.tg` generico alterna `aria-checked`. Zero erros de console/pagina em todas as etapas.
  - **Pendente para depois**: replicar tema/i18n completo em `professor.html`/`diretor.html` (ainda so receberam a correcao pontual de marca).
- [2026-07-29] **Modo claro do aluno recebeu segunda passada de polish** (pedido do Andre: "mais detalhado, mais bonito"). Sombras (`--sh`/`--sh-lg`) com opacidade/alcance maiores, contornos (`--line`/`--line-strong`) mais escuros, textura radial quase imperceptivel no fundo (`--canvas-texture`, so no light - dark fica sem, explicitamente zerada nos dois caminhos escuros para nao vazar). `h1`/`.card>h2`/`.tile .num` em Josefin Sans com mais peso/tamanho. Icones dos tiles de estatistica (`.tile .tico`) ganharam fundo circular lavanda em vez de flutuar soltos em cinza. Verificado por screenshot Playwright nas telas Inicio, Materiais e Simulados - consistente nas tres.
- [2026-07-29] **Tutor de IA (tela imersiva sempre escura) trocou identidade de verde-esmeralda para par roxo-midnight + ciano eletrico**, decisao explicita do Andre ("nao quero lavanda, faz uma cor exclusiva com cara de IA/tecnologia... roxo midnight com neon perolado, eletrico reativo com ciano") - rejeitou tanto manter o verde quanto unificar com a lavanda do resto do app; a tela do Tutor continua com paleta propria, exclusiva, por ser o modo de estudo imersivo. Tokens novos em `assets/ui.css`: `--tut-purple:#7c5cff`/`--tut-purple-deep:#4a2fd9` (base/glow ambiente) e `--tut-cyan:#3ceae0`/`--tut-cyan-deep:#1fb8b0` (acento reativo - hover, envio, foco, badges). `--tut-green*` (usado em >60 lugares do CSS) virou alias do ciano em vez de reescrever cada regra. Fundo (`--tut-bg`) ganhou leve matiz roxo (`#0f0e1a`) em vez de neutro puro - "midnight", nao "preto de TV". Elementos de marca (`.tut-orb`, avatar do tutor; `.tut-send`, botao de enviar) agora usam gradiente ciano->roxo em vez de solido, reforcando o par dicromatico. Cores hardcoded remanescentes (`rgba(62,155,114,...)`, `rgba(47,212,138,...)`, `#08150F`/`#04140D` como texto-sobre-verde) foram migradas para `color-mix(...,var(--tut-cyan)...)` e um verde-escuro compativel (`#052421`), senao ficariam esverdeadas mesmo apos a troca do token. Verificado por screenshot Playwright na conversa do tutor e no painel de configuracoes.

- [2026-07-31] **Favicon do Prisma adicionado em todas as telas do mockup** (pedido do Andre: "coloque o icone correto... nao e mais um teste, agora e serio"). O que estava faltando de fato nao era a marca da sidebar - essa ja usava o `#i-logo` correto desde 2026-07-29 (verificado por leitura do codigo e por screenshot Playwright, identico ao `Logo.tsx`) - e sim o icone da aba do navegador: nenhuma tela do mockup tinha `<link rel="icon">`, entao o Chrome mostrava o icone generico de documento. Criado `mockup/assets/favicon.svg` (mesmo SVG de `frontend/public/favicon.svg`, grafite `#1a1a1a` sobre fundo transparente) e referenciado com `<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">` em `aluno.html`, `professor.html`, `diretor.html`, `index.html`, `login.html`, `criar-conta.html` e `landing.html` (excluido so `app.html`, prototipo antigo fora do escopo de sincronizacao). Sincronizado para `frontend/public/app/` via `scripts/sincronizar-app.py` (16 arquivos). **Verificado via Playwright**: subi a Vite dev server do `frontend/` numa porta separada (5180) porque a 5173 estava ocupada por outro projeto (`Felixo-AI-Core`, processo de outro repositorio rodando em paralelo na maquina) - nao matei aquele processo, so usei outra porta. `link[rel=icon]` resolve para `assets/favicon.svg`, request retorna 200 `image/svg+xml`, zero erros de console. Servidor de verificacao encerrado ao final (processo criado por esta sessao, seguro de parar).
- [2026-07-31] **Varredura visual completa do mockup via Playwright** (pedido do Andre: "continua dando upgrade... baixa uma ferramenta pra tirar print sozinho"). Playwright/Chromium ja estavam instalados em `frontend/` desde 2026-07-29 - nao foi preciso baixar nada novo. Subi o Vite dev server numa porta livre (5182) e tirei ~40 screenshots (light/dark, todas as telas de `aluno.html`/`professor.html`/`diretor.html`, `index.html`, `login.html` por perfil) com um script descartavel (`frontend/qa-screenshots.mjs`, nao commitado). Dois problemas reais encontrados e corrigidos:
  - **`professor.html` ainda usava o vocabulario da era individual** (mesmo residuo de familia do achado da sessao anterior com `criar-conta.html`, ver [[projeto-plataforma-estudos-openrouter]]): nav dizia "Workspaces" em vez de "Turmas", existia uma tela inteira `s-workspace` de "compartilhe seu workspace com um link publico" (qualquer um com o link vira "aluno"), e o cargo de Ricardo Almeida aparecia como "Tutor" em vez de "Professor" (sidebar + modal "Minha conta"). Isso contradizia o resto do proprio produto: `diretor.html` ja mostra 412 contas de aluno pre-existentes geridas pela escola, entao um professor "convidar aluno por link publico" nunca fez sentido num modelo 100% institucional. Corrigido: removida a secao/tela `s-workspace` inteira e o nav "Compartilhar"; "Workspaces" -> "Turmas" em todos os textos (nav, eyebrow, h1, botao "Novo workspace" -> "Configurar nova turma", "compartilhado" -> "alunos matriculados", "Uso do tutor por workspace" -> "...por turma"); "Tutor" -> "Professor" nos dois lugares. Preferencia "Novo acesso ao workspace (notificar quando alguem entrar pelo link)" virou "Novo aluno na turma (notificar quando a secretaria matricular um aluno)". `diretor.html` e `aluno.html` ja estavam limpos (conferido tela por tela) - o padrao correto de convite institucional ja existe em `diretor.html` -> Equipe ("Convidar professor" por e-mail, "Convite pendente").
  - **Bug real e nao relacionado ao pivo, achado por acaso na tela Creditos de IA do diretor**: os numeros "Professores"/"Alunos" apareciam como "10251,782"/"6741,661" em vez de "18.400"/"12.100". Causa: `animarNumero` em `assets/app.js` (contador que anima de 0 ate o valor final) calculava `decimais` com `bruto.split(/[.,]/)[1]`, que trata "." (separador de milhar, `18.400`) igual a "," (separador decimal, `7,9`) - para "18.400" isso da `decimais=3`, entao ao final da animacao o numero fica com 3 casas decimais falsas (`18400,000` em vez de `18.400`), e durante a animacao mostra fracoes sem sentido. So afeta `.hval`/`.tile .num` com 4+ digitos formatados com ponto de milhar (por isso nao aparecia em numeros menores como "407 alunos ativos" ou "62%"). Corrigido: `decimais` agora vem de `bruto.match(/,(\d+)$/)` (so conta virgula final como decimal) e o ramo inteiro usa `Math.round(v).toLocaleString('pt-BR')` (reaplica o separador de milhar) em vez de `String(Math.round(v))`. Verificado via Playwright antes/depois: com a espera da animacao completa (900ms), "18.400"/"12.100"/"500" aparecem corretos.
  - Screenshots ficaram no scratchpad da sessao (nao commitados, nao fazem parte do repo).
- [2026-07-31] **Tema claro/escuro passa a existir em `professor.html` e `diretor.html`** (item 1 da lista de melhorias priorizada com o Andre). Era a maior inconsistencia entre os tres perfis: o aluno tinha o toggle desde 2026-07-29, professor e diretor nao - um diretor logando a noite nao tinha a opcao que um aluno tem. O trabalho pesado ja estava feito: `assets/ui.css` e `assets/app.js` sao compartilhados pelas tres telas e o dark mode ja respondia a `:root[data-theme="dark"]` (confirmado por screenshot antes de mexer, forcando o atributo via JS). Faltava so a interface. Adicionado em cada uma: os symbols `#i-sun`/`#i-moon` (nao existiam nesses dois arquivos), o `<button id="themebtn">` na topbar antes do sino (mesma posicao do aluno) e uma linha "Modo escuro" no modal "Minha conta" com `id="tg-tema"` - o handler generico de `.tg` em `app.js` ja exclui `#tg-tema` de proposito (comentario de 2026-07-29), entao o espelho sincroniza sem handler duplicado. Nenhuma linha de JS nova: `app.js` procura `#themebtn`/`#tg-tema` por id e simplesmente nao achava nessas telas. Sem `data-i18n` porque professor/diretor ainda nao tem i18n - continua pendente. **Verificado via Playwright** nas tres telas: toggle troca `data-theme` light<->dark, icone alterna lua<->sol, persiste apos reload (`localStorage` `prisma-theme`), e o toggle do modal reflete e controla o mesmo estado; zero erros de console.
- [2026-07-31] **Bug de corrupcao permanente nos contadores animados** (`animarNumero` em `assets/app.js`), achado por acaso durante a validacao do tema acima: notei o tile do diretor mostrando "410 alunos ativos" num screenshot e "407" noutro, sendo que o HTML diz **412**. Nao era so captura no meio da animacao - reproduzido com Playwright: em repouso da 412, ida-e-volta lenta entre telas da 412, mas **navegacao rapida (interrompendo a animacao) deixava 212 permanentemente**. Causa: a funcao lia o alvo de `el.textContent` a cada chamada. `animarTela` roda a cada troca de tela (`show()`), entao trocar de tela antes dos 900ms de animacao fazia a segunda chamada adotar o *valor parcial que estava na tela* como novo destino - e o numero nunca mais voltava ao certo. Gravidade real: e um painel de gestao mostrando numero errado sem nenhum sinal de que esta errado. Corrigido em duas partes: (1) o texto original do HTML e guardado em `el._alvoOriginal` na primeira passada e reusado nas seguintes, entao o alvo nunca mais vem de um valor parcial (a precedencia `dataset.valor` continua valendo, e como `definir()` muda estado de verdade); (2) `cancelAnimationFrame` do quadro anterior do mesmo elemento antes de comecar outro, senao dois `requestAnimationFrame` escreveriam por cima um do outro. Propriedade JS (`_alvoOriginal`, `_animId`) em vez de `dataset` de proposito: e bookkeeping interno, nao contrato publico como `data-valor`. **Verificado**: 412 nos tres cenarios (repouso, ida-e-volta, navegacao rapida) e os tiles do aluno seguem estaveis (14 / 6 dias / 8 / 23) sob o mesmo estresse, ja que `app.js` e compartilhado.
- [2026-07-31] **Tutor de IA perdeu a paleta exclusiva (roxo-midnight + ciano) e passou a herdar a paleta Prisma do resto do app**, decisao explicita do Andre pedindo para "refazer no teor e aparencia do projeto" a partir de um screenshot da tela. Pergunta feita antes de mexer, porque o registro de 2026-07-29 documentava a paleta propria como decisao consciente dele mesmo ("nao quero lavanda... roxo midnight com neon perolado"); a resposta confirmou reverter essa decisao, nao só "melhorar a execucao" mantendo a cor. Mudancas em `Estudo-com-IA/mockup/`:
  - **Extracao para modulos proprios**: o bloco do Tutor (~430 linhas) saiu de `assets/ui.css` (1252 linhas, acima do limite de 250 da constituicao de modularidade) para `assets/tutor.css` (barra, mensagens, dock) e `assets/tutor-painel.css` (paineis de Contexto/Configuracoes), carregados depois de `ui.css` em `aluno.html`. `ui.css` caiu para 817 linhas. `.tut-file-spin` ficou em `ui.css` porque `app.js` usa como spinner de botao ocupado em qualquer tela, apesar do nome.
  - **Tokens `--tut-*` viraram apelidos dos tokens globais** (`--tut-bg:var(--canvas)`, `--tut-ink:var(--ink)` etc.) em vez de valores hex proprios - claro/escuro passam a seguir `data-theme` automaticamente, sem nenhuma regra de tema duplicada. So dois valores nao derivam direto de token existente: `--tut-accent-solid`/`--tut-on-accent` (o par solido usado no avatar do tutor, badge do contador e botao "Gerar episodio"), porque a lavanda pura nao tem contraste para essas superficies - resolvido com `#5b58a8`/creme no claro e `#a5a2dc`/grafite no escuro, os mesmos tons que `--green-ink` ja usa no resto do app.
  - **Botoes de acao primaria (enviar mensagem, gerar episodio) migraram de gradiente ciano-roxo para grafite solido** (`var(--ink)`/`var(--canvas)`), seguindo a regra ja escrita em `ui.css` de que acento de perfil nao e CTA universal - a mesma regra que ja regia `.btn-pri` no resto do app so nao tinha sido aplicada nesta tela.
  - **Contraste WCAG medido** (script proprio, luminancia relativa) para os 9 pares novos em cada tema: todos passam 4.5:1 (texto pequeno) ou 3:1 (UI/borda), exceto `--ink-3` sobre `--card` no claro (3.53:1) - token global pre-existente do app, nao introduzido por esta mudanca, fora do escopo desta tarefa.
  - **Dois bugs de CSS achados e corrigidos durante a verificacao visual, nenhum causado pela extracao em si** (ja existiam sob a paleta antiga, so ficaram visiveis ao olhar de novo): (1) `.tmsg.ai .tmsg-bubble b` pintava de acento qualquer `<b>` dentro da bolha da IA, inclusive as letras a/b/c/d das alternativas do quiz - ficavam lavanda por cima do verde/vermelho do estado respondido, ilegiveis; virou `.tmsg.ai .tmsg-bubble>b` (so filho direto) mais `.tmsg-quiz p b` (o destaque do enunciado). (2) `.tut-file-tx span` (descendente, nao filho) quebrava a meta do arquivo em duas linhas ("1,4 MB ·" / "lido pela IA") porque pegava o `<span>` de i18n aninhado tambem; virou `.tut-file-tx>span`.
  - **Bug de layout achado e corrigido, tambem pre-existente**: abaixo de 720px a barra do Tutor pedia 496px de largura e o excedente sumia sem rolagem (cortado pelo `overflow:hidden` do `.content`) - `min-width:auto` de flex item nao contido, o mesmo padrao do `min-height:0` que a tela ja usava no eixo vertical. Corrigido com `min-width:0` na mesma cadeia (`.tut`, `.tut-body`, `.tut-scroll`, `#s-tutor.on`). Rotulos das abas Contexto/Configuracoes tambem viraram texto so-leitor-de-tela abaixo de 720px (mantendo icone + contador visiveis) para caber sem quebrar.
  - **Verificado via Playwright** (nao so lint/build): Vite dev server numa porta livre (5187), screenshots de tela cheia em light/dark, dos dois paineis laterais (Contexto com upload/arquivos/audio-revisao, Configuracoes com segmented controls e toggles), do quiz respondido (certo/errado) e de mobile 390px - confirmando os tres bugs corrigidos e nenhum residuo visual do roxo-ciano antigo (checagem programada por regex de cor, `sobrouCiano:false` nos dois temas). Zero erros de console/pagina. Servidor de verificacao encerrado ao final (processo desta sessao, seguro de parar); scripts `qa-*.mjs` descartaveis, nao commitados.
  - Sincronizado para `frontend/public/app/` via `scripts/sincronizar-app.py` (18 arquivos, dois a mais que antes pelos dois CSS novos).
- [2026-07-31] **Corrigido flash de tema claro (FOUC) em `aluno.html`/`professor.html`/`diretor.html`**. O `app.js` que le `prisma-theme` do `localStorage` e aplica `data-theme` roda no fim do `<body>` - com o escuro salvo, a pagina pintava clara por um instante e so depois trocava, visivel a cada carregamento/reload. Corrigido com um `<script>` inline no `<head>`, antes do `link` do `ui.css`, que aplica `data-theme` cedo (mesma tecnica padrao de anti-flash, ja que o CSS de tema so existe depois desse `<link>`). **Verificado via Playwright**: apos salvar `dark` e recarregar, o fundo computado do `<body>` ja sai escuro (`rgb(21,20,18)`) nas tres telas.

## Registros de 2026-07-29 (bugs e fixes do HUD, `start_app.py`/`scripts/hud/`)

> Movidos de `IA.md` em 2026-08-03, mesmo motivo do bloco acima: passou do teto
> de 400 linhas. Todos sao do mesmo dia, sobre o HUD Tkinter, ja resolvidos e
> sem decisao viva pendente.

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
