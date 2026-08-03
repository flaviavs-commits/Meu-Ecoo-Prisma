/* Casca do modal de Configuracoes: barra lateral com grupos + area de
   conteudo, no molde Linear/Notion (um unico dialogo, secoes trocam por
   dentro - nunca abre um modal novo por secao). Singleton: so existe um
   dialogo de configuracoes por vez, reaberto/trocado de secao conforme
   o gatilho clicado. */
import { abrirDialogo } from './core.js';
import { secoesParaPerfil, GRUPOS } from './registry.js';

let instancia = null;

function svgIcone(id) {
  return '<svg class="ic"><use href="#' + id + '"/></svg>';
}

function montarEsqueleto() {
  return (
    '<div class="pm-skel-linha w-40"></div>' +
    '<div class="pm-skel-bloco"></div>' +
    '<div class="pm-skel-linha w-100"></div>' +
    '<div class="pm-skel-linha w-80"></div>' +
    '<div class="pm-skel-linha w-60"></div>'
  );
}

function criarInstancia(perfil) {
  const secoes = secoesParaPerfil(perfil.tipo);
  const cache = {}; // id -> true depois da primeira renderizacao (evita re-flash do skeleton)
  let secaoAtual = null;

  const dlg = abrirDialogo({
    tamanho: 'shell',
    classe: 'pm-settings',
    rotuloPor: 'pm-settings-titulo',
    aoFechar: function () { instancia = null; },
  });

  dlg.painel.innerHTML =
    '<button type="button" class="pm-close pm-settings-close" data-pm-close aria-label="Fechar">✕</button>' +
    '<div class="pm-settings-shell">' +
      '<aside class="pm-settings-nav">' +
        '<div class="pm-settings-quem">' +
          '<span class="pm-settings-av" style="' + (perfil.cor ? 'background:' + perfil.cor : '') + '">' + (perfil.iniciais || '') + '</span>' +
          '<div><b id="pm-settings-titulo">' + (perfil.nome || '') + '</b><span>' + (perfil.cargo || '') + '</span></div>' +
        '</div>' +
        '<nav class="pm-settings-grupos"></nav>' +
      '</aside>' +
      '<section class="pm-settings-content">' +
        '<div class="pm-settings-content-head">' +
          '<button type="button" class="pm-settings-voltar" data-pm-voltar aria-label="Voltar">' + svgIcone('i-chev') + '<span>Configurações</span></button>' +
        '</div>' +
        '<div class="pm-body pm-settings-body"></div>' +
      '</section>' +
    '</div>';
  dlg.painel.querySelector('.pm-settings-voltar .ic').classList.add('pm-chev-esq');

  const elGrupos = dlg.painel.querySelector('.pm-settings-grupos');
  const elBody = dlg.painel.querySelector('.pm-settings-body');
  const elShell = dlg.painel.querySelector('.pm-settings-shell');

  GRUPOS.forEach(function (grupo) {
    const doGrupo = secoes.filter(function (s) { return s.grupo === grupo.id; });
    if (!doGrupo.length) return;
    const bloco = document.createElement('div');
    bloco.className = 'pm-settings-grupo';
    bloco.innerHTML = '<p class="pm-settings-grupo-rotulo">' + grupo.rotulo + '</p>';
    doGrupo.forEach(function (s) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'pm-settings-item';
      btn.dataset.secao = s.id;
      btn.innerHTML = svgIcone(s.icone) + '<span>' + s.rotulo + '</span>';
      btn.addEventListener('click', function () { abrirSecao(s.id); });
      bloco.appendChild(btn);
    });
    elGrupos.appendChild(bloco);
  });

  function marcarAtivo(id) {
    elGrupos.querySelectorAll('.pm-settings-item').forEach(function (btn) {
      btn.classList.toggle('on', btn.dataset.secao === id);
    });
  }

  function abrirSecao(id) {
    const secao = secoes.filter(function (s) { return s.id === id; })[0];
    if (!secao) return;
    secaoAtual = id;
    marcarAtivo(id);
    elShell.classList.add('pm-mostrar-conteudo');

    if (cache[id]) {
      elBody.innerHTML = '';
      secao.montar(elBody, contexto);
      elBody.scrollTop = 0;
      return;
    }

    elBody.innerHTML = montarEsqueleto();
    elBody.scrollTop = 0;
    var espera = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 320;
    setTimeout(function () {
      if (secaoAtual !== id) return; // a pessoa ja trocou de secao antes do "carregamento" acabar
      cache[id] = true;
      elBody.innerHTML = '';
      secao.montar(elBody, contexto);
    }, espera);
  }

  const contexto = { perfil: perfil, abrirSecao: abrirSecao };

  dlg.painel.querySelector('[data-pm-close]').addEventListener('click', function () { dlg.fechar('fechar'); });
  dlg.painel.querySelector('[data-pm-voltar]').addEventListener('click', function () {
    elShell.classList.remove('pm-mostrar-conteudo');
  });

  return {
    dlg: dlg,
    secoes: secoes,
    abrirSecao: abrirSecao,
  };
}

/** Abre (ou reaproveita) o dialogo de configuracoes na secao pedida. */
export function abrirConfiguracoes(perfil, secaoId) {
  if (!instancia) instancia = criarInstancia(perfil);
  const alvo = secaoId && instancia.secoes.some(function (s) { return s.id === secaoId; }) ? secaoId : instancia.secoes[0].id;
  instancia.abrirSecao(alvo);
}
