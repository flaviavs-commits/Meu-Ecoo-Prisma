/* Navegação entre telas + dropdowns (notificações / conta) */
(function () {
  // Telas
  var links = document.querySelectorAll('[data-s]');
  function show(s) {
    document.querySelectorAll('.screen').forEach(function (x) { x.classList.remove('on'); });
    var el = document.getElementById('s-' + s);
    if (el) { void el.offsetWidth; el.classList.add('on'); }
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

  // Modais (ex.: Minha conta) — sempre centralizados, nunca navegam para uma tela
  var modalBackdrop = document.getElementById('modal-backdrop');
  var openModal = null;
  function closeModal() {
    if (openModal) { openModal.classList.remove('open'); openModal = null; }
    if (modalBackdrop) modalBackdrop.classList.remove('open');
  }
  document.querySelectorAll('[data-modal]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      close(); // fecha qualquer dropdown aberto
      var m = document.getElementById('modal-' + btn.dataset.modal);
      if (!m) return;
      m.classList.add('open');
      openModal = m;
      if (modalBackdrop) modalBackdrop.classList.add('open');
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach(function (btn) {
    btn.addEventListener('click', closeModal);
  });
  if (modalBackdrop) modalBackdrop.addEventListener('click', closeModal);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { close(); closeModal(); }
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
      try { localStorage.setItem(CHAVE, tema); } catch (e) {}
      pintar();
    }
    function alternar() { aplicar(temaAtual() === 'dark' ? 'light' : 'dark'); }

    try {
      var salvo = localStorage.getItem(CHAVE);
      if (salvo) root.dataset.theme = salvo;
    } catch (e) {}
    pintar();

    var themeBtn = document.getElementById('themebtn');
    if (themeBtn) themeBtn.addEventListener('click', alternar);
    if (tgTema) tgTema.addEventListener('click', alternar);
  })();

  // ── Idioma ──
  (function () {
    var opcoes = document.querySelectorAll('.lang-opt');
    if (!opcoes.length) return;
    opcoes.forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (window.PrismaI18n) window.PrismaI18n.setLang(btn.dataset.lang);
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
})();
