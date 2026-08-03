/* Barra lateral do tutor: nova conversa, busca por titulo, favoritas,
   pastas e historico agrupado por data - o mesmo vocabulario visual
   de ChatGPT/Claude/Cursor. So sabe desenhar a lista a partir do
   estado da loja; toda mutacao (criar pasta, favoritar, excluir) e
   feita chamando `core/loja.js` direto, e o re-render vem sozinho
   pela assinatura em `index.js`. */
import * as loja from '../core/loja.js';
import { confirmar } from '../../modal/confirm.js';

const TAGS_DISPONIVEIS = ['ENEM', 'Revisão', 'Dúvida', 'Prioridade'];

function grupoPorData(conversas) {
  const hoje = new Date(); hoje.setHours(0, 0, 0, 0);
  const ontem = hoje.getTime() - 86400000;
  const seteDias = hoje.getTime() - 6 * 86400000;
  const grupos = { Hoje: [], Ontem: [], 'Últimos 7 dias': [], 'Mais antigas': [] };
  conversas.forEach(function (c) {
    if (c.atualizadaEm >= hoje.getTime()) grupos.Hoje.push(c);
    else if (c.atualizadaEm >= ontem) grupos.Ontem.push(c);
    else if (c.atualizadaEm >= seteDias) grupos['Últimos 7 dias'].push(c);
    else grupos['Mais antigas'].push(c);
  });
  return grupos;
}

function linhaConversa(c, ativa) {
  const tags = c.tags.map(function (t) { return '<span class="chat-tag-chip">' + t + '</span>'; }).join('');
  return (
    '<div class="chat-conv-item' + (ativa ? ' on' : '') + '" data-conversa="' + c.id + '" draggable="true">' +
      '<span class="chat-conv-tx">' +
        '<b data-titulo>' + c.titulo + '</b>' +
        (tags ? '<span class="chat-conv-tags">' + tags + '</span>' : '') +
      '</span>' +
      '<span class="chat-conv-acoes">' +
        '<button type="button" class="chat-conv-acao' + (c.favorita ? ' on' : '') + '" data-acao="favoritar" aria-label="Favoritar"><svg class="ic"><use href="#i-star"/></svg></button>' +
        '<button type="button" class="chat-conv-acao" data-acao="tag" aria-label="Etiquetas"><svg class="ic"><use href="#i-tag"/></svg></button>' +
        '<button type="button" class="chat-conv-acao" data-acao="excluir" aria-label="Excluir"><svg class="ic"><use href="#i-trash"/></svg></button>' +
      '</span>' +
    '</div>'
  );
}

export function criarBarraLateral(container, ctx) {
  container.innerHTML =
    '<div class="chat-side-topo">' +
      '<button type="button" class="chat-side-nova"><svg class="ic"><use href="#i-plus"/></svg><span>Nova conversa</span></button>' +
      '<div class="chat-side-busca"><svg class="ic"><use href="#i-search"/></svg><input type="text" placeholder="Buscar conversas…" aria-label="Buscar conversas"></div>' +
    '</div>' +
    '<div class="chat-side-lista"></div>' +
    '<div class="chat-side-pastas-nova"><button type="button"><svg class="ic"><use href="#i-folder"/></svg><span>Nova pasta</span></button></div>';

  const lista = container.querySelector('.chat-side-lista');
  const buscaInput = container.querySelector('.chat-side-busca input');
  let filtro = '';

  container.querySelector('.chat-side-nova').addEventListener('click', function () {
    ctx.aoNovaConversa();
  });
  container.querySelector('.chat-side-pastas-nova button').addEventListener('click', function () {
    const nome = window.prompt('Nome da pasta:');
    if (nome) loja.criarPastaNaLoja(nome);
  });
  buscaInput.addEventListener('input', function () {
    filtro = buscaInput.value.trim().toLowerCase();
    renderizarLista(loja.obterEstado());
  });

  function conversasFiltradas(estado) {
    if (!filtro) return estado.conversas;
    return estado.conversas.filter(function (c) {
      return c.titulo.toLowerCase().includes(filtro) ||
        c.mensagens.some(function (m) { return m.texto.toLowerCase().includes(filtro); });
    });
  }

  function renderizarSecao(titulo, conversas, ativaId, idPastaVazia) {
    if (!conversas.length && !idPastaVazia) return '';
    const corpo = conversas.length
      ? conversas.map(function (c) { return linhaConversa(c, c.id === ativaId); }).join('')
      : '<p class="chat-side-pasta-vazia">Arraste uma conversa pra cá.</p>';
    return '<p class="chat-side-rotulo"' + (idPastaVazia ? ' data-pasta-alvo="' + idPastaVazia + '"' : '') + '>' + titulo + '</p>' + corpo;
  }

  function renderizarLista(estado) {
    const conversas = conversasFiltradas(estado);
    const favoritas = conversas.filter(function (c) { return c.favorita; });
    const semPasta = conversas.filter(function (c) { return !c.pastaId; });
    const grupos = grupoPorData(semPasta);

    let html = '';
    if (favoritas.length) html += renderizarSecao('Favoritas', favoritas, estado.conversaAtivaId);

    // Pastas aparecem mesmo vazias - senao criar uma pasta parece nao ter
    // feito nada, sem nenhum lugar pra confirmar que ela existe.
    estado.pastas.forEach(function (p) {
      const daPasta = conversas.filter(function (c) { return c.pastaId === p.id; });
      html += renderizarSecao(p.nome, daPasta, estado.conversaAtivaId, p.id);
    });

    ['Hoje', 'Ontem', 'Últimos 7 dias', 'Mais antigas'].forEach(function (chave) {
      html += renderizarSecao(chave, grupos[chave], estado.conversaAtivaId);
    });

    if (!conversas.length) {
      html = '<div class="pm-vazio" style="padding:30px 14px"><span class="pm-vazio-ic"><svg class="ic"><use href="#i-search"/></svg></span><b>Nada encontrado</b><span>Tente outro termo.</span></div>';
    }
    lista.innerHTML = html;
    ligarLinhas();
  }

  function ligarLinhas() {
    lista.querySelectorAll('.chat-conv-item').forEach(function (linha) {
      const id = linha.dataset.conversa;

      linha.addEventListener('click', function (e) {
        // So as acoes (favoritar/tag/excluir) e o input de renomear ja aberto
        // cancelam a selecao - clicar no titulo em si tambem seleciona a
        // conversa (o duplo-clique de renomear e um listener a parte, os
        // dois convivem sem conflito).
        if (e.target.closest('.chat-conv-acao') || e.target.tagName === 'INPUT') return;
        ctx.aoSelecionarConversa(id);
      });

      const titulo = linha.querySelector('[data-titulo]');
      titulo.addEventListener('dblclick', function (e) {
        e.stopPropagation();
        const atual = titulo.textContent;
        const input = document.createElement('input');
        input.className = 'chat-conv-renomear';
        input.value = atual;
        titulo.replaceWith(input);
        input.focus();
        input.select();
        function confirmarNome() { loja.renomearConversa(id, input.value || atual); }
        input.addEventListener('blur', confirmarNome);
        input.addEventListener('keydown', function (ev) {
          if (ev.key === 'Enter') input.blur();
          if (ev.key === 'Escape') { input.value = atual; input.blur(); }
        });
      });

      linha.querySelector('[data-acao="favoritar"]').addEventListener('click', function (e) {
        e.stopPropagation();
        const c = loja.obterConversa(id);
        loja.favoritarConversa(id, !c.favorita);
      });

      linha.querySelector('[data-acao="excluir"]').addEventListener('click', function (e) {
        e.stopPropagation();
        const c = loja.obterConversa(id);
        confirmar({
          titulo: 'Excluir "' + c.titulo + '"?',
          descricao: 'As mensagens desta conversa serão perdidas.',
          rotuloConfirmar: 'Excluir',
          perigo: true,
        }).then(function (ok) { if (ok) loja.excluirConversa(id); });
      });

      linha.querySelector('[data-acao="tag"]').addEventListener('click', function (e) {
        e.stopPropagation();
        abrirMenuTags(linha, id);
      });

      linha.addEventListener('dragstart', function (e) {
        e.dataTransfer.setData('text/conversa-id', id);
      });
    });

    // Pastas recebem conversas soltas por cima (drag&drop simples entre
    // secoes) - soltar num rotulo com pasta move pra ela, soltar em
    // qualquer outro rotulo tira a conversa de pasta nenhuma.
    lista.querySelectorAll('.chat-side-rotulo').forEach(function (rotulo) {
      rotulo.addEventListener('dragover', function (e) { e.preventDefault(); rotulo.classList.add('chat-side-rotulo-alvo'); });
      rotulo.addEventListener('dragleave', function () { rotulo.classList.remove('chat-side-rotulo-alvo'); });
      rotulo.addEventListener('drop', function (e) {
        e.preventDefault();
        rotulo.classList.remove('chat-side-rotulo-alvo');
        const idSolto = e.dataTransfer.getData('text/conversa-id');
        if (!idSolto) return;
        loja.moverParaPasta(idSolto, rotulo.dataset.pastaAlvo || null);
      });
    });
  }

  function abrirMenuTags(linha, idConversa) {
    lista.querySelectorAll('.chat-tags-menu').forEach(function (m) { m.remove(); });
    const c = loja.obterConversa(idConversa);
    const menu = document.createElement('div');
    menu.className = 'chat-tags-menu';
    menu.innerHTML = TAGS_DISPONIVEIS.map(function (t) {
      const ativa = c.tags.indexOf(t) !== -1;
      return '<button type="button" class="' + (ativa ? 'on' : '') + '" data-tag="' + t + '">' + t + '</button>';
    }).join('');
    linha.appendChild(menu);
    menu.addEventListener('click', function (e) {
      e.stopPropagation();
      const btn = e.target.closest('[data-tag]');
      if (!btn) return;
      loja.alternarTag(idConversa, btn.dataset.tag);
    });
    setTimeout(function () {
      document.addEventListener('click', function fechar() {
        menu.remove();
        document.removeEventListener('click', fechar);
      }, { once: true });
    }, 0);
  }

  return { renderizar: renderizarLista };
}
