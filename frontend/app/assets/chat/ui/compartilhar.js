/* Folha de compartilhamento de uma mensagem ou conversa. Sem backend
   neste repositorio o link e ilustrativo (gerado no cliente, nunca
   resolve de verdade) - mas o fluxo inteiro existe: gerar, copiar,
   avisar que copiou. */
import { abrirDialogo } from '../../modal/core.js';
import { avisar } from '../../modal/toast.js';

function linkFalso(idConversa) {
  return 'https://prisma.app/c/' + idConversa.replace(/^c_/, '').slice(0, 10);
}

/** @param {{titulo:string, idConversa:string, texto:string}} alvo */
export function abrirCompartilhar(alvo) {
  const dlg = abrirDialogo({ tamanho: 'sm', rotuloPor: 'chat-compart-titulo' });
  const link = linkFalso(alvo.idConversa);

  dlg.painel.innerHTML =
    '<div class="pm-head"><div class="pm-head-tx"><h3 id="chat-compart-titulo">Compartilhar</h3><p>' + alvo.titulo + '</p></div>' +
      '<button type="button" class="pm-close" data-fechar aria-label="Fechar">✕</button></div>' +
    '<div class="pm-body">' +
      '<div class="field"><label>Link de visualização</label>' +
        '<div class="pm-key-row"><span class="pm-key-valor" style="flex:1">' + link + '</span>' +
        '<button type="button" class="pm-key-ico-btn" data-copiar-link aria-label="Copiar link"><svg class="ic"><use href="#i-copy"/></svg></button></div>' +
      '</div>' +
      '<div class="pm-acoes-dir" style="margin-top:16px;justify-content:flex-start;gap:8px">' +
        '<button type="button" class="btn btn-gho btn-sm" data-copiar="markdown"><svg class="ic"><use href="#i-doc"/></svg><span>Copiar como Markdown</span></button>' +
        '<button type="button" class="btn btn-gho btn-sm" data-copiar="texto"><svg class="ic"><use href="#i-copy"/></svg><span>Copiar texto puro</span></button>' +
      '</div>' +
    '</div>';

  dlg.painel.querySelector('[data-fechar]').addEventListener('click', function () { dlg.fechar('fechar'); });
  dlg.painel.querySelector('[data-copiar-link]').addEventListener('click', function (e) {
    if (navigator.clipboard) navigator.clipboard.writeText(link).catch(function () {});
    avisar('Link copiado', 'ok');
    e.currentTarget.classList.add('pm-copiado');
  });
  dlg.painel.querySelector('[data-copiar="markdown"]').addEventListener('click', function () {
    if (navigator.clipboard) navigator.clipboard.writeText(alvo.texto).catch(function () {});
    avisar('Copiado como Markdown', 'ok');
  });
  dlg.painel.querySelector('[data-copiar="texto"]').addEventListener('click', function () {
    const semMarkdown = alvo.texto.replace(/[`*_#>]/g, '');
    if (navigator.clipboard) navigator.clipboard.writeText(semMarkdown).catch(function () {});
    avisar('Texto copiado', 'ok');
  });
}
