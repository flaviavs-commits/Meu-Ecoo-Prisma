/* Dialogo de confirmacao (neutro ou perigoso) - construido em cima do
   motor generico de core.js. Usado por qualquer acao destrutiva ou que
   mereca uma pausa antes de executar (encerrar sessao, remover
   dispositivo, excluir conta, revogar chave...). Uma unica implementacao
   para nao ter um `confirm()` nativo do navegador furando a identidade
   visual em algum canto do produto. */
import { abrirDialogo } from './core.js';

let seq = 0;

/**
 * @param {{
 *   titulo:string, descricao?:string,
 *   rotuloConfirmar?:string, rotuloCancelar?:string,
 *   perigo?:boolean,
 *   textoParaDigitar?:string,
 *   aoConfirmar?:() => Promise<void>|void,
 * }} opcoes
 * @returns {Promise<boolean>} true se confirmado (e aoConfirmar nao lancou erro)
 */
export function confirmar(opcoes) {
  const o = opcoes || {};
  const idTitulo = 'pm-conf-titulo-' + (++seq);

  return new Promise(function (resolve) {
    const dlg = abrirDialogo({
      tamanho: 'sm',
      rotuloPor: idTitulo,
      classe: 'pm-confirma' + (o.perigo ? ' pm-confirma-perigo' : ''),
      aoFechar: function () { resolve(false); },
    });

    const head = document.createElement('div');
    head.className = 'pm-head';
    head.innerHTML =
      '<div class="pm-confirma-ic"><svg class="ic"><use href="#' + (o.perigo ? 'i-alert' : 'i-check') + '"/></svg></div>' +
      '<div class="pm-head-tx"><h3 id="' + idTitulo + '"></h3></div>';
    head.querySelector('h3').textContent = o.titulo || 'Confirmar acao';
    dlg.painel.appendChild(head);

    const body = document.createElement('div');
    body.className = 'pm-body';
    if (o.descricao) {
      const p = document.createElement('p');
      p.className = 'pm-confirma-desc';
      p.textContent = o.descricao;
      body.appendChild(p);
    }

    let campoDigitar = null;
    if (o.textoParaDigitar) {
      const wrap = document.createElement('div');
      wrap.className = 'field';
      wrap.style.marginTop = '14px';
      wrap.innerHTML =
        '<label>Digite <b>' + o.textoParaDigitar + '</b> para confirmar</label>' +
        '<input class="input" type="text" autocomplete="off" spellcheck="false">';
      campoDigitar = wrap.querySelector('input');
      body.appendChild(wrap);
    }
    dlg.painel.appendChild(body);

    const foot = document.createElement('div');
    foot.className = 'pm-foot';
    foot.innerHTML =
      '<button type="button" class="btn btn-gho" data-acao="cancelar"></button>' +
      '<button type="button" class="btn ' + (o.perigo ? 'btn-danger' : 'btn-pri') + '" data-acao="confirmar"></button>';
    const btnCancelar = foot.querySelector('[data-acao="cancelar"]');
    const btnConfirmar = foot.querySelector('[data-acao="confirmar"]');
    btnCancelar.textContent = o.rotuloCancelar || 'Cancelar';
    btnConfirmar.textContent = o.rotuloConfirmar || (o.perigo ? 'Excluir' : 'Confirmar');
    dlg.painel.appendChild(foot);

    function sincronizarPortao() {
      if (!campoDigitar) return;
      const ok = campoDigitar.value.trim().toUpperCase() === o.textoParaDigitar.toUpperCase();
      btnConfirmar.disabled = !ok;
      btnConfirmar.classList.toggle('pm-btn-desabilitado', !ok);
    }
    if (campoDigitar) {
      sincronizarPortao();
      campoDigitar.addEventListener('input', sincronizarPortao);
      campoDigitar.setAttribute('data-pm-foco-inicial', '');
    }

    btnCancelar.addEventListener('click', function () { dlg.fechar('cancelar'); });

    btnConfirmar.addEventListener('click', function () {
      if (btnConfirmar.disabled) return;
      const rotuloOriginal = btnConfirmar.innerHTML;
      btnConfirmar.innerHTML = '<span class="tut-file-spin"></span>' + (o.rotuloCarregando || 'Processando…');
      btnConfirmar.disabled = true;
      btnCancelar.disabled = true;
      dlg.definirCarregando(true);

      Promise.resolve()
        .then(function () { return o.aoConfirmar ? o.aoConfirmar() : undefined; })
        .then(function () {
          resolve(true);
          dlg.fechar('confirmado');
        })
        .catch(function (erro) {
          dlg.definirCarregando(false);
          btnConfirmar.disabled = false;
          btnCancelar.disabled = false;
          btnConfirmar.innerHTML = rotuloOriginal;
          let banner = body.querySelector('.pm-banner-erro');
          if (!banner) {
            banner = document.createElement('div');
            banner.className = 'pm-banner pm-banner-erro';
            banner.innerHTML = '<svg class="ic"><use href="#i-alert"/></svg><span></span>';
            body.appendChild(banner);
          }
          banner.querySelector('span').textContent = (erro && erro.message) || 'Nao foi possivel concluir. Tente novamente.';
        });
    });
  });
}
