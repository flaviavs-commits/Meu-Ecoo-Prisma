/* Command palette global do mockup. Descobre as ações de navegação já
   existentes no DOM, então não mantém um segundo catálogo de rotas. */
(function () {
  'use strict';
  var painel;
  function fechar() { if (!painel) return; painel.remove(); painel = null; }
  function abrir() {
    if (painel) { fechar(); return; }
    painel = document.createElement('div');
    painel.className = 'cmd-backdrop';
    painel.innerHTML = '<section class="cmd-palette" role="dialog" aria-modal="true" aria-labelledby="cmd-title"><div class="cmd-search"><span aria-hidden="true">⌘</span><input id="cmd-input" type="search" placeholder="Ir para uma tela ou ação…" autocomplete="off"><kbd>Esc</kbd></div><h2 id="cmd-title" class="sr-only">Comandos rápidos</h2><div class="cmd-results" role="listbox"></div><p class="cmd-hint">↑↓ navegar · Enter abrir · Esc fechar</p></section>';
    document.body.appendChild(painel);
    var input = painel.querySelector('#cmd-input');
    var resultados = painel.querySelector('.cmd-results');
    var acoes = Array.prototype.slice.call(document.querySelectorAll('[data-s]')).filter(function (el) { return el.textContent.trim() && el.offsetParent !== null; }).slice(0, 30);
    var dados = acoes.map(function (el) { return { texto: el.textContent.trim().replace(/\s+/g, ' '), destino: el.dataset.s, elemento: el }; });
    var indice = 0;
    function renderizar() {
      var q = input.value.trim().toLowerCase();
      var filtradas = dados.filter(function (item) { return !q || item.texto.toLowerCase().indexOf(q) !== -1; });
      indice = Math.min(indice, Math.max(0, filtradas.length - 1));
      resultados.innerHTML = filtradas.map(function (item, i) { return '<button type="button" role="option" class="cmd-item' + (i === indice ? ' on' : '') + '" data-cmd-index="' + i + '"><span>' + item.texto + '</span><kbd>↵</kbd></button>'; }).join('') || '<p class="cmd-empty">Nenhum comando encontrado.</p>';
      resultados.querySelectorAll('.cmd-item').forEach(function (botao) { botao.addEventListener('click', function () { filtradas[Number(botao.dataset.cmdIndex)].elemento.click(); fechar(); }); });
    }
    input.addEventListener('input', renderizar);
    input.addEventListener('keydown', function (event) { var itens = resultados.querySelectorAll('.cmd-item'); if (event.key === 'ArrowDown') { event.preventDefault(); indice = Math.min(indice + 1, itens.length - 1); renderizar(); } if (event.key === 'ArrowUp') { event.preventDefault(); indice = Math.max(indice - 1, 0); renderizar(); } if (event.key === 'Enter' && itens[indice]) itens[indice].click(); if (event.key === 'Escape') fechar(); });
    painel.addEventListener('mousedown', function (event) { if (event.target === painel) fechar(); });
    renderizar(); input.focus();
  }
  document.addEventListener('keydown', function (event) { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); abrir(); } if (event.key === 'Escape' && painel) fechar(); });
  window.PrismaCommandPalette = { open: abrir, close: fechar };
}());
