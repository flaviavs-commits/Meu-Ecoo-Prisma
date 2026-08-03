/* Busca global (Cmd/Ctrl+K): pesquisa titulo e conteudo de TODAS as
   conversas do tutor, nao so a aberta - o mesmo padrao de command
   palette do Cursor/Linear. Construida em cima do motor generico de
   dialogo de assets/modal/, para herdar foco preso/ESC/blur de graca. */
import { abrirDialogo } from '../../modal/core.js';
import * as loja from '../core/loja.js';

function trechoComTermo(conversa, termo) {
  const m = conversa.mensagens.find(function (x) { return x.texto.toLowerCase().includes(termo); });
  if (!m) return null;
  const i = m.texto.toLowerCase().indexOf(termo);
  const inicio = Math.max(0, i - 24);
  return (inicio > 0 ? '…' : '') + m.texto.slice(inicio, i + termo.length + 40) + '…';
}

export function abrirPaletaComandos(aoEscolherConversa) {
  const dlg = abrirDialogo({ tamanho: 'md', classe: 'chat-paleta', rotuloPor: 'chat-paleta-titulo' });

  dlg.painel.innerHTML =
    '<div class="chat-paleta-busca">' +
      '<svg class="ic"><use href="#i-search"/></svg>' +
      '<input type="text" id="chat-paleta-titulo" placeholder="Buscar em todas as conversas…" autocomplete="off">' +
      '<kbd>esc</kbd>' +
    '</div>' +
    '<div class="chat-paleta-resultados"></div>';

  const input = dlg.painel.querySelector('input');
  const resultados = dlg.painel.querySelector('.chat-paleta-resultados');
  let selecionado = 0;
  let itens = [];

  function renderizar() {
    const termo = input.value.trim().toLowerCase();
    const todas = loja.todasAsConversas();
    itens = !termo
      ? todas.slice(0, 8)
      : todas.filter(function (c) {
          return c.titulo.toLowerCase().includes(termo) || c.mensagens.some(function (m) { return m.texto.toLowerCase().includes(termo); });
        });

    if (!itens.length) {
      resultados.innerHTML = '<div class="pm-vazio" style="padding:30px 14px"><b>Nada encontrado</b><span>Tente outro termo.</span></div>';
      return;
    }

    resultados.innerHTML = itens.map(function (c, i) {
      const trecho = termo ? trechoComTermo(c, termo) : null;
      return (
        '<button type="button" class="chat-paleta-item' + (i === selecionado ? ' on' : '') + '" data-i="' + i + '">' +
          '<svg class="ic"><use href="#i-message"/></svg>' +
          '<span><b>' + c.titulo + '</b>' + (trecho ? '<small>' + trecho + '</small>' : '') + '</span>' +
        '</button>'
      );
    }).join('');
  }

  function escolher(i) {
    const c = itens[i];
    if (!c) return;
    aoEscolherConversa(c.id);
    dlg.fechar('escolhido');
  }

  input.addEventListener('input', function () { selecionado = 0; renderizar(); });
  resultados.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-i]');
    if (btn) escolher(Number(btn.dataset.i));
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); selecionado = Math.min(itens.length - 1, selecionado + 1); renderizar(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); selecionado = Math.max(0, selecionado - 1); renderizar(); }
    else if (e.key === 'Enter') { e.preventDefault(); escolher(selecionado); }
  });

  renderizar();
}
