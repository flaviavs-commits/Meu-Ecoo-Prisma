/* Atalhos de teclado do tutor: wiring global + a folha de ajuda
   (Cmd/Ctrl+/) que lista todos eles - sem essa folha, um atalho que
   ninguem lembra pra que serve. */
import { abrirDialogo } from '../../modal/core.js';

const MAC = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
const MOD = MAC ? '⌘' : 'Ctrl';

const LISTA = [
  // Cmd/Ctrl+K sozinho ja abre o navegador de telas de assets/command-palette.js
  // (global, do mockup inteiro) - a busca de conversas usa Shift a mais para nao brigar com ele.
  { teclas: [MOD, '⇧', 'K'], desc: 'Buscar em todas as conversas' },
  { teclas: [MOD, 'N'], desc: 'Nova conversa' },
  { teclas: [MOD, 'B'], desc: 'Mostrar/ocultar barra lateral' },
  { teclas: [MOD, 'F'], desc: 'Buscar na conversa aberta' },
  { teclas: ['Enter'], desc: 'Enviar mensagem' },
  { teclas: ['Shift', 'Enter'], desc: 'Nova linha na mensagem' },
  { teclas: ['Esc'], desc: 'Parar geração / fechar busca' },
  { teclas: [MOD, '/'], desc: 'Esta ajuda' },
];

/**
 * @param {{abrirPaleta, novaConversa, alternarSidebar, abrirBusca}} acoes
 */
export function ligarAtalhosGlobais(acoes) {
  document.addEventListener('keydown', function (e) {
    const tutorAberto = document.getElementById('s-tutor');
    if (!tutorAberto || !tutorAberto.classList.contains('on')) return;
    const mod = e.metaKey || e.ctrlKey;
    if (!mod) return;

    // Shift+K, nao so K: Cmd/Ctrl+K sozinho ja e o navegador de telas global
    // (assets/command-palette.js) - sem o Shift os dois disputariam o mesmo atalho.
    if (e.shiftKey && e.key.toLowerCase() === 'k') { e.preventDefault(); acoes.abrirPaleta(); }
    else if (e.key.toLowerCase() === 'n') { e.preventDefault(); acoes.novaConversa(); }
    else if (e.key.toLowerCase() === 'b') { e.preventDefault(); acoes.alternarSidebar(); }
    else if (e.key.toLowerCase() === 'f') { e.preventDefault(); acoes.abrirBusca(); }
    else if (e.key === '/') { e.preventDefault(); abrirAjudaAtalhos(); }
  });
}

export function abrirAjudaAtalhos() {
  const dlg = abrirDialogo({ tamanho: 'sm', rotuloPor: 'chat-atalhos-titulo' });
  dlg.painel.innerHTML =
    '<div class="pm-head"><div class="pm-head-tx"><h3 id="chat-atalhos-titulo">Atalhos de teclado</h3></div>' +
      '<button type="button" class="pm-close" data-fechar aria-label="Fechar">✕</button></div>' +
    '<div class="pm-body">' +
      '<div class="chat-atalhos-lista">' +
        LISTA.map(function (a) {
          return '<div class="chat-atalho-linha"><span>' + a.desc + '</span><span class="chat-atalho-teclas">' +
            a.teclas.map(function (t) { return '<kbd>' + t + '</kbd>'; }).join('<i>+</i>') +
            '</span></div>';
        }).join('') +
      '</div>' +
    '</div>';
  dlg.painel.querySelector('[data-fechar]').addEventListener('click', function () { dlg.fechar('fechar'); });
}
