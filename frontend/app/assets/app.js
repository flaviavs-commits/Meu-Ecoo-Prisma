/* Navegação entre telas + dropdowns (notificações / conta) */
(function () {

  // ══════════════════════════════════════════════════════════════════
  // Infraestrutura compartilhada: toast, contadores animados e estado
  // ══════════════════════════════════════════════════════════════════

  var reduzMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Aviso flutuante. Mock nao tem backend, entao toda acao que "salva"
     ou "gera" precisa de uma confirmacao visivel - sem isso o clique
     parece nao ter funcionado. */
  var toastHost = null;
  function toast(texto, tipo) {
    if (!toastHost) {
      toastHost = document.createElement('div');
      toastHost.className = 'toast-host';
      document.body.appendChild(toastHost);
    }
    var el = document.createElement('div');
    el.className = 'toast' + (tipo ? ' toast-' + tipo : '');
    el.setAttribute('role', 'status');
    el.textContent = texto;
    toastHost.appendChild(el);
    setTimeout(function () { el.classList.add('out'); }, 2600);
    setTimeout(function () { el.remove(); }, 3000);
  }

  function toastUndo(texto, desfazer) {
    if (!toastHost) { toastHost = document.createElement('div'); toastHost.className = 'toast-host'; document.body.appendChild(toastHost); }
    var el = document.createElement('div'); el.className = 'toast toast-ok toast-undo'; el.setAttribute('role', 'status');
    var mensagem = document.createElement('span'); mensagem.textContent = texto; el.appendChild(mensagem);
    var botao = document.createElement('button'); botao.type = 'button'; botao.className = 'toast-undo-btn'; botao.textContent = 'Desfazer';
    botao.addEventListener('click', function () { if (typeof desfazer === 'function') desfazer(); el.remove(); }); el.appendChild(botao); toastHost.appendChild(el);
    setTimeout(function () { el.classList.add('out'); }, 5200); setTimeout(function () { el.remove(); }, 5600);
  }

  /* Conta de 0 ate o valor final. Guarda o texto original para preservar
     sufixo/prefixo ("6 dias", "92%") - so o numero anima. */
  function animarNumero(el) {
    // O alvo precisa vir de uma fonte estavel. Ler `textContent` a cada
    // chamada quebrava quando a funcao rodava de novo com uma animacao
    // ainda em voo: o alvo virava o valor parcial que estava na tela, e
    // o numero ficava permanentemente errado - trocar de tela rapido
    // fazia "412 alunos ativos" virar "212". Por isso o texto do HTML e
    // guardado na primeira passada e reusado nas seguintes.
    if (el._alvoOriginal === undefined) el._alvoOriginal = el.textContent;
    var alvo = el.dataset.valor !== undefined ? el.dataset.valor : el._alvoOriginal;
    var m = String(alvo).match(/-?[\d.,]+/);
    if (!m) return;
    var bruto = m[0];
    var destino = parseFloat(bruto.replace(/\./g, '').replace(',', '.'));
    if (isNaN(destino)) return;
    // So conta como decimal a virgula final ("7,9"): o ponto e separador
    // de milhar ("18.400"), nao casa de decimal - split(/[.,]/) tratava os
    // dois igual e inflava "18.400" para 3 casas decimais falsas (virava
    // "18400,000" ao fim da animacao em vez de manter "18.400").
    var decimais = (bruto.match(/,(\d+)$/) || ['', ''])[1].length;
    var antes = String(alvo).slice(0, m.index);
    var depois = String(alvo).slice(m.index + bruto.length);

    function escrever(v) {
      var txt = decimais ? v.toFixed(decimais).replace('.', ',') : Math.round(v).toLocaleString('pt-BR');
      el.textContent = antes + txt + depois;
    }
    if (reduzMovimento) { escrever(destino); return; }

    // Duas animacoes no mesmo elemento se atropelariam, cada uma
    // escrevendo por cima da outra a cada quadro.
    if (el._animId) cancelAnimationFrame(el._animId);

    var inicio = performance.now(), dur = 900;
    function passo(agora) {
      var t = Math.min(1, (agora - inicio) / dur);
      escrever(destino * (1 - Math.pow(1 - t, 3)));  // easeOutCubic
      el._animId = t < 1 ? requestAnimationFrame(passo) : null;
    }
    el._animId = requestAnimationFrame(passo);
  }

  /* Roda os contadores e as barras da tela que acabou de abrir. As
     barras usam --w (largura final) ja no HTML; aqui so disparamos a
     transicao a partir de zero. */
  function animarTela(tela) {
    if (!tela) return;
    tela.querySelectorAll('.tile .num').forEach(animarNumero);
    tela.querySelectorAll('.hval').forEach(animarNumero);
    if (reduzMovimento) return;
    tela.querySelectorAll('.hbar i, .chart .b i').forEach(function (barra) {
      var final = barra.style.getPropertyValue('--w') || barra.style.getPropertyValue('--h');
      var prop = barra.style.getPropertyValue('--w') ? '--w' : '--h';
      if (!final) return;
      barra.style.setProperty(prop, '0%');
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { barra.style.setProperty(prop, final); });
      });
    });
  }

  /* Estado do aluno compartilhado entre as abas. Os tiles da tela
     Inicio leem daqui, entao concluir um simulado numa aba reflete na
     outra - sem isso os numeros seriam texto morto no HTML. */
  var estado = {
    sessoes: 14,
    simulados: 8,
    materiais: 23,
    creditos: 86,
  };
  function definir(chave, valor) {
    estado[chave] = valor;
    document.querySelectorAll('[data-estado="' + chave + '"]').forEach(function (el) {
      el.dataset.valor = String(valor);
      animarNumero(el);
    });
  }
  function somar(chave, delta) { definir(chave, (estado[chave] || 0) + delta); }

  // Telas
  var links = document.querySelectorAll('[data-s]');
  function show(s) {
    document.querySelectorAll('.screen').forEach(function (x) { x.classList.remove('on'); });
    var el = document.getElementById('s-' + s);
    if (el) { void el.offsetWidth; el.classList.add('on'); animarTela(el); }
    document.querySelectorAll('.nav a[data-s]').forEach(function (a) {
      a.classList.toggle('on', a.dataset.s === s);
    });
    window.scrollTo({ top: 0, behavior: 'instant' });
  }
  links.forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (a.tagName === 'A') e.preventDefault();
      show(a.dataset.s);
    });
  });

  // Dropdowns
  var open = null;
  var backdrop = document.getElementById('dd-backdrop');
  function close() {
    if (open) { open.classList.remove('open'); open = null; }
    if (backdrop) backdrop.classList.remove('open');
  }
  document.querySelectorAll('[data-dd]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var dd = document.getElementById(btn.dataset.dd);
      if (!dd) return;
      if (open === dd) { close(); return; }
      close();
      dd.classList.add('open');
      open = dd;
      if (backdrop) backdrop.classList.add('open');
      var nd = btn.querySelector('.ndot');
      if (nd) nd.remove();
    });
  });
  if (backdrop) backdrop.addEventListener('click', close);
  document.addEventListener('click', function (e) {
    if (open && !open.contains(e.target)) close();
  });

  // Modal de Configuracoes (Perfil, Seguranca, etc.): sistema proprio em
  // assets/modal/, carregado como modulo ES a parte - so falta fechar o
  // dropdown quando ESC tambem deve fechar um dialogo dele (o proprio
  // motor do modal cuida do resto).
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') close();
  });

  // Conversas (mensagens)
  document.querySelectorAll('.convo button').forEach(function (b) {
    b.addEventListener('click', function () {
      b.closest('.convo').querySelectorAll('button').forEach(function (x) { x.classList.remove('on'); });
      b.classList.add('on');
      var u = b.querySelector('.unread');
      if (u) u.remove();
    });
  });

  // Toggles genericos (agora <button role="switch">, nao mais <span>
  // decorativo). #tg-tema fica de fora daqui - e o espelho do tema real
  // e recebe o clique da funcao de tema (mais abaixo), senao os dois
  // handlers brigariam pelo mesmo estado.
  document.querySelectorAll('.tg').forEach(function (t) {
    if (t.id === 'tg-tema') return;
    t.addEventListener('click', function () {
      var ligado = t.classList.toggle('off') === false;
      t.setAttribute('aria-checked', String(ligado));
    });
  });

  // ── Tema claro/escuro ──
  // Mesmo padrao ja usado em mockup/app.html: prefers-color-scheme como
  // fallback, data-theme no <html> forcando a escolha explicita quando a
  // pessoa troca manualmente, persistido em localStorage.
  (function () {
    var root = document.documentElement;
    var themeIc = document.getElementById('theme-ic');
    var tgTema = document.getElementById('tg-tema');
    var CHAVE = 'prisma-theme';

    function temaAtual() {
      return root.dataset.theme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    }
    function pintar() {
      var escuro = temaAtual() === 'dark';
      if (themeIc) themeIc.innerHTML = '<use href="#i-' + (escuro ? 'sun' : 'moon') + '"/>';
      if (tgTema) {
        tgTema.classList.toggle('off', !escuro);
        tgTema.setAttribute('aria-checked', String(escuro));
      }
    }
    function aplicar(tema) {
      root.dataset.theme = tema;
      try { localStorage.setItem(CHAVE, tema); } catch {}
      pintar();
    }
    function alternar() { aplicar(temaAtual() === 'dark' ? 'light' : 'dark'); }

    try {
      var salvo = localStorage.getItem(CHAVE);
      if (salvo) root.dataset.theme = salvo;
    } catch {}
    pintar();

    var themeBtn = document.getElementById('themebtn');
    if (themeBtn) themeBtn.addEventListener('click', alternar);
    if (tgTema) tgTema.addEventListener('click', alternar);

    // Exposicao para o sistema de modais (secao Preferencias) controlar
    // o mesmo tema por fora desta IIFE, sem duplicar a logica acima.
    window.PrismaTheme = { atual: temaAtual, aplicar: aplicar };
  })();

  // ── Idioma ──
  (function () {
    var opcoes = document.querySelectorAll('.lang-opt');
    if (!opcoes.length) return;
    opcoes.forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (window.PrismaI18n) window.PrismaI18n.setLang(btn.dataset.lang);
        close();
      });
    });
  })();

  // Biblioteca de materiais: busca + filtro + ordenação (funcional)
  var grid = document.getElementById('lib-grid');
  if (grid) {
    var input = document.getElementById('lib-search');
    var wrap = document.getElementById('lib-search-wrap');
    var clearBtn = document.getElementById('lib-clear');
    var chips = document.querySelectorAll('.filter .chip[data-f]');
    var countEl = document.getElementById('lib-count');
    var countLabelEl = document.getElementById('lib-count-label');
    var emptyEl = document.getElementById('lib-empty');
    var sortBtn = document.getElementById('lib-sortbtn');
    var sortMenu = document.getElementById('lib-sortmenu');
    var sortLabel = document.getElementById('lib-sortlabel');
    var items = Array.prototype.slice.call(grid.querySelectorAll('.mat'));
    var state = { q: '', kind: 'todos', sort: 'recent' };
    // Chaves do dicionario i18n, nao mais texto fixo em portugues - com
    // 5 idiomas, "6 materiais" e o rotulo de ordenacao tinham que mudar
    // junto quando a pessoa troca de idioma, e um objeto fixo nunca ia
    // acompanhar isso.
    var sortChaves = { recent: 'materiais.maisRecentes', old: 'materiais.maisAntigos', az: 'materiais.nomeAZ' };

    function apply() {
      var q = state.q.trim().toLowerCase();
      var visible = items.filter(function (el) {
        var matchesKind = state.kind === 'todos' || el.dataset.kind === state.kind;
        var matchesQ = !q || el.dataset.name.indexOf(q) !== -1;
        var show = matchesKind && matchesQ;
        el.classList.toggle('hide', !show);
        return show;
      });

      var sorted = visible.slice().sort(function (a, b) {
        if (state.sort === 'az') return a.dataset.name.localeCompare(b.dataset.name);
        var da = a.dataset.date, db = b.dataset.date;
        return state.sort === 'old' ? da.localeCompare(db) : db.localeCompare(da);
      });
      sorted.forEach(function (el) { grid.appendChild(el); });

      countEl.textContent = String(visible.length);
      countLabelEl.setAttribute('data-i18n', visible.length === 1 ? 'materiais.contagemSingular' : 'materiais.contagemPlural');
      if (window.PrismaI18n) window.PrismaI18n.aplicarEm(countLabelEl);
      emptyEl.classList.toggle('show', visible.length === 0);
      grid.style.display = visible.length === 0 ? 'none' : '';
      wrap.classList.toggle('has-val', q.length > 0);
    }

    input.addEventListener('input', function () { state.q = input.value; apply(); });
    clearBtn.addEventListener('click', function () { input.value = ''; state.q = ''; apply(); input.focus(); });

    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        chips.forEach(function (x) { x.classList.remove('on'); });
        c.classList.add('on');
        state.kind = c.dataset.f;
        apply();
      });
    });

    sortBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      sortMenu.classList.toggle('open');
    });
    sortMenu.querySelectorAll('button').forEach(function (b) {
      b.addEventListener('click', function () {
        state.sort = b.dataset.sort;
        sortLabel.setAttribute('data-i18n', sortChaves[state.sort]);
        if (window.PrismaI18n) window.PrismaI18n.aplicarEm(sortLabel);
        sortMenu.querySelectorAll('button').forEach(function (x) { x.classList.remove('on'); });
        b.classList.add('on');
        sortMenu.classList.remove('open');
        apply();
      });
    });
    document.addEventListener('click', function (e) {
      if (!sortMenu.contains(e.target) && e.target !== sortBtn) sortMenu.classList.remove('open');
    });

    apply();
  }

  // Assistente da biblioteca: chips preenchem o campo de comando
  var libaiInput = document.querySelector('.libai-composer input');
  document.querySelectorAll('.libai-chips button').forEach(function (b) {
    b.addEventListener('click', function () {
      if (libaiInput) {
        libaiInput.value = b.textContent.trim();
        libaiInput.focus();
      }
    });
  });

  // ── Tutor de IA: abas laterais (Contexto / Configurações) + drop de arquivos ──
  var ctxBody = document.getElementById('tut-body');
  if (ctxBody) {
    var tabs = ctxBody.parentElement.querySelectorAll('.tut-tab');
    var ctxCount = ctxBody.parentElement.querySelector('.tut-tab .tut-ctx-count');

    function syncTabs() {
      var open = ctxBody.getAttribute('data-open') || '';
      tabs.forEach(function (t) {
        t.setAttribute('aria-expanded', String(t.dataset.panel === open));
      });
    }
    function openPanel(name) {
      var cur = ctxBody.getAttribute('data-open') || '';
      if (cur === name) { ctxBody.removeAttribute('data-open'); }  // clicar de novo fecha
      else { ctxBody.setAttribute('data-open', name); }
      syncTabs();
    }
    function closePanel() { ctxBody.removeAttribute('data-open'); syncTabs(); }

    tabs.forEach(function (t) {
      t.addEventListener('click', function () { openPanel(t.dataset.panel); });
    });
    // Botões ✕ dentro de cada painel
    ctxBody.querySelectorAll('.tut-ctx-close').forEach(function (b) {
      b.addEventListener('click', closePanel);
    });
    // No overlay (telas médias), clicar no backdrop fecha
    ctxBody.addEventListener('click', function (e) {
      if (window.innerWidth <= 1100 && ctxBody.getAttribute('data-open')) {
        if (!e.target.closest('.tut-ctx')) closePanel();
      }
    });
    // Esc fecha o painel
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && ctxBody.getAttribute('data-open')) closePanel();
    });
    syncTabs();

    // Accordion exclusivo: abrir uma seção fecha as outras (divide o vertical)
    var secs = ctxBody.querySelectorAll('.tut-sec');
    secs.forEach(function (sec) {
      sec.addEventListener('toggle', function () {
        if (sec.open) secs.forEach(function (o) { if (o !== sec) o.open = false; });
      });
    });

    // Configurações: segmented controls e toggles
    ctxBody.querySelectorAll('.tut-seg').forEach(function (seg) {
      seg.addEventListener('click', function (e) {
        var btn = e.target.closest('button');
        if (!btn) return;
        seg.querySelectorAll('button').forEach(function (b) { b.classList.remove('on'); });
        btn.classList.add('on');
      });
    });
    ctxBody.querySelectorAll('.tut-sw').forEach(function (sw) {
      sw.addEventListener('click', function () {
        var on = sw.classList.toggle('on');
        sw.setAttribute('aria-checked', String(on));
      });
    });

    // ── Episódios / áudio-revisão (seção dentro do painel de Contexto) ──
    var epPanel = ctxBody.querySelector('.tut-ep');
    if (epPanel) {
      var picks = epPanel.querySelectorAll('.tut-pick-item input');
      var pickCount = epPanel.querySelector('.tut-pick-count b');
      var epGen = document.getElementById('tut-ep-gen');
      var epList = epPanel.querySelector('.tut-ep-list');

      function updatePicks() {
        var n = 0;
        picks.forEach(function (p) { if (p.checked) n++; });
        if (pickCount) pickCount.textContent = String(n);
        if (epGen) epGen.disabled = n === 0;
      }
      picks.forEach(function (p) { p.addEventListener('change', updatePicks); });
      updatePicks();

      var PLAY = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l11-6.5z"/></svg>';
      var PAUSE = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>';

      // Play/pause — só um tocando por vez
      if (epList) {
        epList.addEventListener('click', function (e) {
          var btn = e.target.closest('.tut-ep-play');
          if (!btn) return;
          var wasPlaying = btn.classList.contains('playing');
          epList.querySelectorAll('.tut-ep-play.playing').forEach(function (b) {
            b.classList.remove('playing'); b.innerHTML = PLAY;
          });
          if (!wasPlaying) { btn.classList.add('playing'); btn.innerHTML = PAUSE; }
        });
      }

      // Gerar: estado de loading e novo item no topo da lista
      if (epGen) {
        epGen.addEventListener('click', function () {
          if (epGen.disabled) return;
          var label = epGen.innerHTML;
          epGen.disabled = true;
          epGen.innerHTML = '<span class="tut-file-spin"></span>Gerando episódio…';
          setTimeout(function () {
            var fmt = epPanel.querySelector('.tut-seg button.on');
            var fmtTx = fmt ? fmt.textContent.toLowerCase() : 'diálogo';
            var el = document.createElement('div');
            el.className = 'tut-ep-item';
            el.innerHTML =
              '<button class="tut-ep-play" aria-label="Reproduzir">' + PLAY + '</button>' +
              '<div class="tut-ep-tx"><b>Novo episódio — ' + fmtTx + '</b><span>agora · 7:30</span></div>' +
              '<span class="tut-ep-dur">7:30</span>';
            if (epList) epList.prepend(el);
            epGen.disabled = false;
            epGen.innerHTML = label;
          }, 1800);
        });
      }
    }

    // Drop de arquivos (demonstração)
    var drop = document.getElementById('tut-drop');
    var fileInput = drop && drop.querySelector('input[type=file]');
    var fileList = document.querySelector('.tut-files');

    function iconFor(name) {
      return /\.(png|jpe?g|gif|webp)$/i.test(name) ? '#i-book' : '#i-doc';
    }
    function fmtSize(bytes) {
      if (bytes >= 1048576) return (bytes / 1048576).toFixed(1).replace('.', ',') + ' MB';
      if (bytes >= 1024) return Math.round(bytes / 1024) + ' KB';
      return bytes + ' B';
    }
    var secFilesCount = ctxBody.querySelector('.tut-sec .tut-sec-count');
    function updateCount() {
      if (!fileList) return;
      var n = String(fileList.children.length);
      if (ctxCount) ctxCount.textContent = n;
      if (secFilesCount) secFilesCount.textContent = n;
    }
    function addFile(name, size) {
      if (!fileList) return;
      var el = document.createElement('div');
      el.className = 'tut-file loading';
      el.innerHTML =
        '<span class="tut-file-ic"><svg><use href="' + iconFor(name) + '"/></svg></span>' +
        '<div class="tut-file-tx"><b></b><span>analisando…</span></div>' +
        '<span class="tut-file-spin"></span>';
      el.querySelector('b').textContent = name;
      fileList.prepend(el);
      updateCount();
      // Simula a IA "lendo" o arquivo
      setTimeout(function () {
        el.classList.remove('loading');
        el.querySelector('.tut-file-tx span').textContent = fmtSize(size) + ' · lido pela IA';
        var spin = el.querySelector('.tut-file-spin');
        var x = document.createElement('button');
        x.className = 'tut-file-x'; x.setAttribute('aria-label', 'Remover'); x.textContent = '✕';
        if (spin) spin.replaceWith(x);
      }, 1400);
    }

    // Remover arquivo (delegação — cobre os existentes e os novos)
    if (fileList) {
      fileList.addEventListener('click', function (e) {
        var x = e.target.closest('.tut-file-x');
        if (x) { x.closest('.tut-file').remove(); updateCount(); }
      });
    }

    if (drop) {
      drop.addEventListener('dragover', function (e) { e.preventDefault(); drop.classList.add('drag'); });
      drop.addEventListener('dragleave', function () { drop.classList.remove('drag'); });
      drop.addEventListener('drop', function (e) {
        e.preventDefault(); drop.classList.remove('drag');
        var files = e.dataTransfer && e.dataTransfer.files;
        if (files) for (var i = 0; i < files.length; i++) addFile(files[i].name, files[i].size);
      });
      if (fileInput) fileInput.addEventListener('change', function () {
        for (var i = 0; i < this.files.length; i++) addFile(this.files[i].name, this.files[i].size);
        this.value = '';
      });
    }
    updateCount();
  }

  // ══════════════════════════════════════════════════════════════════
  // Acoes que antes nao respondiam ao clique
  // ══════════════════════════════════════════════════════════════════

  /* Botao "trabalhando": desabilita, troca o rotulo por um spinner e
     devolve o original no fim. Todo fluxo de gerar usa isto, para o
     resultado aparecer depois de uma espera - nunca instantaneo. */
  function comCarregando(btn, rotulo, ms, aoTerminar) {
    if (!btn || btn.disabled) return;
    var original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="tut-file-spin"></span>' + rotulo;
    setTimeout(function () {
      btn.disabled = false;
      btn.innerHTML = original;
      if (aoTerminar) aoTerminar();
    }, ms || 1500);
  }

  // Chat do Tutor, quiz, materias, acoes rapidas e historico: sistema
  // proprio em assets/chat/ (motor de streaming, multiplas conversas,
  // busca, pastas, tags) - carregado como modulo ES a parte.

  // ── Listas navegáveis (Próximos, últimos simulados, agenda) ──
  /* Cada item vira um alvo real: leva para a aba correspondente em vez
     de ser um <li> decorativo. */
  document.querySelectorAll('[data-ir]').forEach(function (el) {
    el.addEventListener('click', function () { show(el.dataset.ir); });
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(el.dataset.ir); }
    });
  });

  // ── Materiais: gerar novo, assistente e abrir card ──
  var grade = document.getElementById('lib-grid');
  function novoMaterial(titulo, materia, icone) {
    if (!grade) return;
    var el = document.createElement('div');
    el.className = 'mat';
    el.dataset.kind = 'gerado';
    el.dataset.name = (titulo + ' ' + materia).toLowerCase();
    el.dataset.date = new Date().toISOString().slice(0, 10);
    el.innerHTML =
      '<span class="mic"><svg class="ic"><use href="#i-' + icone + '"/></svg></span>' +
      '<b></b><span></span><span class="pill p-ia">gerado por IA</span>' +
      '<span class="mdate">agora</span>';
    el.querySelector('b').textContent = titulo;
    el.querySelectorAll('span')[1].textContent = materia;
    grade.prepend(el);
    somar('materiais', 1);
    toast(titulo + ' criado');
  }

  document.querySelectorAll('[data-gerar]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var tipo = btn.dataset.gerar;
      var mapa = {
        resumo: ['Resumo — Orações reduzidas', 'Português', 'doc'],
        flashcards: ['Flashcards — Orações reduzidas', 'Português · 24 cartões', 'cards'],
        audio: ['Áudio — Orações reduzidas', 'Português · 7 min', 'audio'],
        material: ['Resumo — Análise sintática', 'Português', 'doc'],
      };
      var m = mapa[tipo] || mapa.material;
      show('materiais');
      var alvo = document.querySelector('#s-materiais .phead .btn-pri') || btn;
      comCarregando(alvo, 'Gerando…', 1600, function () {
        novoMaterial(m[0], m[1], m[2]);
      });
    });
  });

  var libaiBtn = document.querySelector('.libai-composer button');
  var libaiInp = document.querySelector('.libai-composer input');
  if (libaiBtn && libaiInp) {
    libaiBtn.addEventListener('click', function () {
      if (!libaiInp.value.trim()) { libaiInp.focus(); return; }
      comCarregando(libaiBtn, '', 1200, function () {
        toast('Biblioteca organizada por matéria');
        libaiInp.value = '';
      });
    });
    libaiInp.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); libaiBtn.click(); }
    });
  }

  if (grade) {
    grade.addEventListener('click', function (e) {
      var mat = e.target.closest('.mat');
      if (mat) toast('Abrindo "' + mat.querySelector('b').textContent + '"');
    });
  }

  // ── Simulados: gerar, editar meta e selects ──
  var gerarSim = document.getElementById('sim-gerar');
  if (gerarSim) gerarSim.addEventListener('click', function () {
    comCarregando(gerarSim, 'Gerando simulado…', 1800, function () {
      somar('simulados', 1);
      somar('creditos', -4);
      var hist = document.querySelector('#s-simulados .hrow');
      if (hist) {
        var novo = hist.cloneNode(true);
        novo.querySelector('.hlbl').textContent = 'Português · agora';
        novo.querySelector('.hbar i').style.setProperty('--w', '0%');
        novo.querySelector('.hval').textContent = '—';
        hist.parentElement.prepend(novo);
      }
      toast('Simulado gerado · 15 questões', 'ok');
    });
  });

  // ── Professor: gerar/publicar prova, confirmar correção ──
  // Antes destes ids, esses botoes eram decorativos - nenhum clique tinha
  // qualquer efeito (nem toast), diferente do resto do app do aluno onde
  // toda acao de "gerar" ja respondia.
  var gerarProva = document.getElementById('prova-gerar');
  if (gerarProva) gerarProva.addEventListener('click', function () {
    comCarregando(gerarProva, 'Gerando prova…', 1800, function () {
      toast('Prova gerada · 12 questões', 'ok');
    });
  });

  var publicarProva = document.getElementById('prova-publicar');
  if (publicarProva) publicarProva.addEventListener('click', function () {
    comCarregando(publicarProva, 'Publicando…', 1000, function () {
      toast('Prova publicada para a turma', 'ok');
    });
  });

  var confirmarNota = document.getElementById('correcao-confirmar');
  if (confirmarNota) confirmarNota.addEventListener('click', function () {
    comCarregando(confirmarNota, 'Confirmando…', 700, function () {
      var fila = document.getElementById('correcao-queue');
      var atual = fila && fila.querySelector('li');
      if (atual) atual.remove();
      var restantes = fila ? fila.querySelectorAll('li').length : 0;
      ['correcao-badge', 'correcao-pendentes-pill'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.textContent = String(restantes);
      });
      var proximo = fila && fila.querySelector('li button');
      if (proximo) proximo.classList.add('on');
      else confirmarNota.disabled = true; // fila vazia: nao ha mais o que confirmar
      toast('Nota confirmada · 7,0', 'ok');
    });
  });

  // ── Diretor: gerar relatorio ──
  var gerarRelatorio = document.getElementById('relatorio-gerar');
  if (gerarRelatorio) gerarRelatorio.addEventListener('click', function () {
    comCarregando(gerarRelatorio, 'Gerando relatório…', 1800, function () {
      var lista = document.getElementById('relatorios-lista');
      var primeiro = lista && lista.querySelector('.rrow');
      if (lista && primeiro) {
        var novo = primeiro.cloneNode(true);
        novo.querySelector('b').textContent = 'Desempenho por turma — agora';
        novo.querySelector('.end').innerHTML = '<span class="pill p-ia">gerado</span>';
        lista.insertBefore(novo, primeiro);
      }
      toast('Relatório gerado', 'ok');
    });
  });

  document.querySelectorAll('.selectbox').forEach(function (sel) {
    sel.addEventListener('click', function () { toast('Configuração salva'); });
  });

  var editarMeta = document.querySelector('[data-i18n="simulados.editarMeta"]');
  if (editarMeta) editarMeta.addEventListener('click', function () {
    toast('Edição de meta chega na próxima versão');
  });

  // ── Agenda: navegar entre semanas ──
  (function () {
    var titulo = document.querySelector('#s-agenda h1');
    var btns = document.querySelectorAll('#s-agenda .actions .btn');
    if (!titulo || btns.length < 2) return;
    var semanas = [
      'Semana de 22 a 26 de julho',
      'Semana de 29 de julho a 2 de agosto',
      'Semana de 5 a 9 de agosto',
    ];
    var atual = 1;
    function pintar() {
      titulo.textContent = semanas[atual];
      btns[0].disabled = atual === 0;
      btns[1].disabled = atual === semanas.length - 1;
    }
    btns[0].addEventListener('click', function () { if (atual > 0) { atual--; pintar(); } });
    btns[1].addEventListener('click', function () { if (atual < semanas.length - 1) { atual++; pintar(); } });
    pintar();
  })();

  // Exposicao minima para o sistema de modais (assets/modal/), que roda
  // como modulo ES a parte e por isso nao enxerga o escopo desta IIFE -
  // reusa o mesmo toast e o mesmo padrao de botao ocupado em vez de
  // duplicar os dois. (window.PrismaTheme e exposto dentro do proprio
  // IIFE de tema, mais acima, onde `temaAtual`/`aplicar` existem.)
  window.PrismaToast = toast;
  window.PrismaToastUndo = toastUndo;
  window.PrismaCarregando = comCarregando;

  // Anima a tela que ja esta aberta no carregamento
  animarTela(document.querySelector('.screen.on'));
})();
