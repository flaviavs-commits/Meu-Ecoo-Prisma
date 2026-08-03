/* Interações compartilhadas dos dashboards.
   O mockup usa dados locais, mas este módulo já define o contrato visual para
   loading, erro, vazio e leitura acessível dos gráficos sem duplicar código
   nas três páginas de perfil. */
(function () {
  'use strict';

  function tornarGraficoAcessivel(grafico) {
    var barras = grafico.querySelectorAll('.b');
    barras.forEach(function (barra, indice) {
      var valor = barra.querySelector('b');
      var rotulo = grafico.parentElement.querySelector('.xlabels');
      var label = rotulo && rotulo.children[indice] ? rotulo.children[indice].textContent.trim() : 'período ' + (indice + 1);
      barra.setAttribute('role', 'img');
      barra.setAttribute('aria-label', label + ': ' + (valor ? valor.textContent.trim() : 'sem valor'));
      barra.tabIndex = 0;
    });
  }

  function inicializar() {
    document.querySelectorAll('.dashboard').forEach(function (dashboard) {
      var cabecalho = dashboard.querySelector('.dashboard-header');
      if (!cabecalho || cabecalho.querySelector('.dashboard-period')) return;
      var periodos = document.createElement('div');
      periodos.className = 'dashboard-period';
      periodos.setAttribute('role', 'group');
      periodos.setAttribute('aria-label', 'Período do painel');
      ['7 dias', '30 dias', 'Semestre'].forEach(function (rotulo, indice) {
        var botao = document.createElement('button');
        botao.type = 'button';
        botao.className = 'dashboard-period-item' + (indice === 1 ? ' on' : '');
        botao.textContent = rotulo;
        botao.setAttribute('aria-pressed', indice === 1 ? 'true' : 'false');
        botao.addEventListener('click', function () {
          periodos.querySelectorAll('.dashboard-period-item').forEach(function (item) {
            item.classList.remove('on');
            item.setAttribute('aria-pressed', 'false');
          });
          botao.classList.add('on');
          botao.setAttribute('aria-pressed', 'true');
          dashboard.dispatchEvent(new CustomEvent('prisma:dashboard-periodo', { detail: { periodo: rotulo } }));
        });
        periodos.appendChild(botao);
      });
      cabecalho.querySelector('.actions')?.before(periodos);
    });
    document.querySelectorAll('.dashboard .chart').forEach(tornarGraficoAcessivel);
    document.querySelectorAll('.dashboard .tile').forEach(function (tile) {
      tile.setAttribute('tabindex', '0');
      tile.setAttribute('role', 'group');
    });
  }

  window.PrismaDashboard = {
    loading: function (ativo) {
      document.querySelectorAll('.dashboard').forEach(function (dashboard) {
        dashboard.classList.toggle('dashboard-loading', Boolean(ativo));
        dashboard.setAttribute('aria-busy', ativo ? 'true' : 'false');
      });
    },
    vazio: function (ativo, mensagem) {
      document.querySelectorAll('.dashboard').forEach(function (dashboard) {
        dashboard.classList.toggle('dashboard-empty', Boolean(ativo));
        var aviso = dashboard.querySelector('.dashboard-empty-state');
        if (ativo && !aviso) {
          aviso = document.createElement('div');
          aviso.className = 'dashboard-empty-state';
          aviso.setAttribute('role', 'status');
          aviso.textContent = mensagem || 'Nenhum dado disponível neste período.';
          dashboard.appendChild(aviso);
        }
        if (!ativo && aviso) aviso.remove();
      });
    }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', inicializar);
  else inicializar();
}());
