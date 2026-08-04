/* Ponto de entrada do chat premium do Tutor de IA: le o DOM ja
   existente em #s-tutor (aluno.html), monta a barra lateral, o
   composer, liga a assinatura da loja e os atalhos globais. So roda
   se a tela do tutor existir na pagina. */
import * as loja from './core/loja.js';
import { enviarTurno, cancelarTurno, haTurnoEmAndamento } from './core/turno.js';
import { criarAcoesMensagem } from './core/acoesMensagem.js';
import { montarMensagem, atualizarBolhaStreaming } from './ui/mensagem.js';
import { criarComposer } from './ui/composer.js';
import { criarRolagemInteligente } from './ui/rolagem.js';
import { criarBuscaConversa } from './ui/busca.js';
import { criarBarraLateral } from './ui/barraLateral.js';
import { abrirPaletaComandos } from './ui/paletaComandos.js';
import { montarStatusModelo } from './ui/statusModelo.js';
import { ligarAtalhosGlobais, abrirAjudaAtalhos } from './ui/atalhosAjuda.js';

function iniciar() {
  const secaoTutor = document.getElementById('s-tutor');
  if (!secaoTutor) return;

  const corpo = document.getElementById('tut-body');
  const fluxo = document.getElementById('tut-flow');
  const rolagemEl = document.getElementById('tut-scroll');
  const chatHost = document.querySelector('.tut-chat');
  const ladoEl = document.getElementById('chat-side');
  const dockEl = document.getElementById('tut-dock');
  const buscaBarEl = document.getElementById('chat-busca-bar');
  const statusHost = document.getElementById('chat-status');

  let elMensagens = {};
  let idConversaRenderizada = null;

  const rolagemCtrl = criarRolagemInteligente(rolagemEl, chatHost);
  const buscaCtrl = criarBuscaConversa(fluxo, buscaBarEl);
  const statusCtrl = montarStatusModelo(statusHost);

  function conversaAtualId() { return loja.obterEstado().conversaAtivaId; }

  function renderizarConversaCompleta() {
    const conversa = loja.conversaAtiva();
    fluxo.innerHTML = '';
    elMensagens = {};
    if (!conversa || !conversa.mensagens.length) {
      fluxo.innerHTML =
        '<div class="pm-vazio" style="padding:60px 20px">' +
          '<span class="pm-vazio-ic"><svg class="ic"><use href="#i-message"/></svg></span>' +
          '<b>Comece a conversa</b><span>Mande a primeira mensagem pro tutor desta matéria.</span>' +
        '</div>';
    } else {
      conversa.mensagens.forEach(function (m) {
        const el = montarMensagem(m, acoes);
        fluxo.appendChild(el);
        elMensagens[m.id] = el;
      });
    }
    rolagemCtrl.irParaOFundo(false);
  }

  let elDigitando = null;
  function mostrarDigitando() {
    elDigitando = document.createElement('div');
    elDigitando.className = 'tmsg ai';
    elDigitando.innerHTML = '<span class="tmsg-av"><svg><use href="#i-spark"/></svg></span><div class="tmsg-bubble"><span class="typing-dots"><i></i><i></i><i></i></span></div>';
    fluxo.appendChild(elDigitando);
    rolagemCtrl.aoConteudoMudar();
  }
  function esconderDigitando() {
    if (elDigitando) { elDigitando.remove(); elDigitando = null; }
  }

  const ganchosTurno = {
    aoCriarMensagemUsuario: function (msg) {
      const el = montarMensagem(msg, acoes);
      fluxo.appendChild(el);
      elMensagens[msg.id] = el;
      rolagemCtrl.aoConteudoMudar();
    },
    aoIniciarResposta: function () {
      statusCtrl.definirOcupado(true);
      composerCtrl.atualizarEstadoBotao();
      mostrarDigitando();
    },
    aoCriarMensagemIA: function (msg) {
      esconderDigitando();
      const el = montarMensagem(msg, acoes);
      fluxo.appendChild(el);
      elMensagens[msg.id] = el;
      rolagemCtrl.aoConteudoMudar();
      composerCtrl.atualizarEstadoBotao();
    },
    aoAtualizarTexto: function (msg, parcial) {
      const el = elMensagens[msg.id];
      if (el) atualizarBolhaStreaming(el, parcial, msg.citacoes);
      rolagemCtrl.aoConteudoMudar();
    },
    aoConcluir: function (msgFinal) {
      statusCtrl.definirOcupado(false);
      composerCtrl.atualizarEstadoBotao();
      const elAntigo = elMensagens[msgFinal.id];
      if (elAntigo) {
        const novo = montarMensagem(msgFinal, acoes);
        elAntigo.replaceWith(novo);
        elMensagens[msgFinal.id] = novo;
      }
    },
  };

  const acoes = criarAcoesMensagem({
    idConversaAtual: conversaAtualId,
    rerenderizarConversa: renderizarConversaCompleta,
    ganchosTurno: ganchosTurno,
  });

  const composerCtrl = criarComposer(dockEl, {
    aoEnviar: function (texto, anexos) {
      enviarTurno(conversaAtualId(), texto, anexos, ganchosTurno);
    },
    aoParar: function () { cancelarTurno(); },
    estaRespondendo: haTurnoEmAndamento,
  });

  const barraLateralCtrl = criarBarraLateral(ladoEl, {
    aoNovaConversa: function () {
      const materiaAtiva = document.querySelector('.tut-sub.on');
      loja.novaConversa(materiaAtiva ? materiaAtiva.dataset.materia : 'geral');
      abrirLado(true);
    },
    aoSelecionarConversa: function (id) { loja.ativarConversa(id); },
  });

  // ── Assinatura central: sidebar sempre re-renderiza; o fluxo de
  // mensagens so re-renderiza por completo quando a conversa ATIVA muda -
  // atualizacoes de streaming chegam por fora, via `ganchosTurno`. ──
  loja.assinar(function (estado) {
    barraLateralCtrl.renderizar(estado);
    if (estado.conversaAtivaId !== idConversaRenderizada) {
      idConversaRenderizada = estado.conversaAtivaId;
      renderizarConversaCompleta();
      sincronizarAbaMateria();
    }
  });

  function sincronizarAbaMateria() {
    const conversa = loja.conversaAtiva();
    if (!conversa) return;
    document.querySelectorAll('.tut-sub').forEach(function (b) {
      b.classList.toggle('on', b.dataset.materia === conversa.materiaId);
    });
  }

  // ── Abas de materia: cada uma e uma conversa (cria na primeira vez) ──
  document.querySelectorAll('.tut-sub').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (haTurnoEmAndamento()) return;
      const materiaId = btn.dataset.materia;
      const existente = loja.todasAsConversas().find(function (c) { return c.materiaId === materiaId; });
      if (existente) loja.ativarConversa(existente.id);
      else loja.novaConversa(materiaId, 'Nova conversa');
    });
  });

  // ── Barra lateral: abrir/fechar ──
  function abrirLado(aberta) {
    corpo.setAttribute('data-side', aberta ? 'aberta' : '');
    const btn = document.querySelector('.tut-hist');
    if (btn) btn.setAttribute('aria-pressed', String(aberta));
  }
  const btnLado = document.querySelector('.tut-hist');
  if (btnLado) btnLado.addEventListener('click', function () {
    abrirLado(corpo.getAttribute('data-side') !== 'aberta');
  });

  // ── Busca global (Cmd+K) e ajuda de atalhos ──
  const btnCmdk = document.querySelector('.tut-cmdk-btn');
  if (btnCmdk) btnCmdk.addEventListener('click', function () {
    abrirPaletaComandos(function (id) { loja.ativarConversa(id); });
  });
  const btnAjuda = document.querySelector('.tut-ajuda-btn');
  if (btnAjuda) btnAjuda.addEventListener('click', abrirAjudaAtalhos);

  ligarAtalhosGlobais({
    abrirPaleta: function () { abrirPaletaComandos(function (id) { loja.ativarConversa(id); }); },
    novaConversa: function () {
      const materiaAtiva = document.querySelector('.tut-sub.on');
      loja.novaConversa(materiaAtiva ? materiaAtiva.dataset.materia : 'geral');
    },
    alternarSidebar: function () { abrirLado(corpo.getAttribute('data-side') !== 'aberta'); },
    abrirBusca: function () { buscaCtrl.alternar(); },
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', iniciar);
} else {
  iniciar();
}
