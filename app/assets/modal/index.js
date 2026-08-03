/* Ponto de entrada do sistema de modais: le o perfil da pagina atual
   (definido inline em cada HTML, antes deste script) e liga qualquer
   elemento `[data-settings-open]` para abrir a secao correspondente do
   modal de Configuracoes. */
import { abrirConfiguracoes } from './settings.js';

function fecharDropdownsAbertos() {
  document.querySelectorAll('.dd.open').forEach(function (dd) { dd.classList.remove('open'); });
  var backdrop = document.getElementById('dd-backdrop');
  if (backdrop) backdrop.classList.remove('open');
}

function iniciar() {
  var perfil = window.PRISMA_PERFIL;
  if (!perfil) {
    console.warn('[modal] window.PRISMA_PERFIL nao definido - configure antes de carregar assets/modal/index.js');
    return;
  }

  document.querySelectorAll('[data-settings-open]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      fecharDropdownsAbertos();
      abrirConfiguracoes(perfil, el.dataset.settingsOpen || undefined);
    });
  });

  window.PrismaSettings = {
    open: function (secaoId) { abrirConfiguracoes(perfil, secaoId); },
  };
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', iniciar);
} else {
  iniciar();
}
