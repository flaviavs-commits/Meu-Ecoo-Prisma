/* Secao "Plano e assinatura" (workspace, so diretor): plano atual da
   instituicao e o uso das tres cotas que ele concede. */
const USO = [
  { rotulo: 'Créditos de IA', usado: 31000, total: 50000, sufixo: '' },
  { rotulo: 'Licenças de professores', usado: 32, total: 40, sufixo: '' },
  { rotulo: 'Alunos matriculados', usado: 412, total: 500, sufixo: '' },
];

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Plano e assinatura</h2>' +
      '<p>O plano contratado pela instituição e o uso das cotas atuais.</p>' +
    '</div>' +
    '<div class="card hero" style="margin-bottom:18px">' +
      '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:14px;flex-wrap:wrap">' +
        '<div>' +
          '<p class="eyebrow" style="margin-bottom:6px">Plano atual</p>' +
          '<div class="pm-plano-preco">R$ 1.890<small> /mês</small></div>' +
          '<p style="font-size:12.5px;color:var(--ink-2);margin:4px 0 0">Institucional Plus · renova em 12 de setembro</p>' +
        '</div>' +
        '<span class="pill p-ok">Ativo</span>' +
      '</div>' +
      '<div style="display:flex;gap:9px;margin-top:16px;flex-wrap:wrap">' +
        '<button type="button" class="btn btn-gho btn-sm" data-acao="ver-planos">Ver outros planos</button>' +
        '<button type="button" class="btn btn-pri btn-sm" data-acao="creditos-extra"><svg class="ic"><use href="#i-coin"/></svg><span>Comprar créditos extras</span></button>' +
      '</div>' +
    '</div>' +
    '<h3 class="pm-subtitulo">Uso do ciclo atual</h3>' +
    USO.map(function (u) {
      const pct = Math.round((u.usado / u.total) * 100);
      return (
        '<div class="pm-uso">' +
          '<div class="pm-uso-linha"><span>' + u.rotulo + '</span><b>' + u.usado.toLocaleString('pt-BR') + ' / ' + u.total.toLocaleString('pt-BR') + '</b></div>' +
          '<div class="hbar' + (pct > 85 ? ' bad' : '') + '"><i style="--w:' + pct + '%"></i></div>' +
        '</div>'
      );
    }).join('');

  container.querySelector('[data-acao="ver-planos"]').addEventListener('click', function () {
    if (window.PrismaToast) window.PrismaToast('Comparativo de planos ainda não está disponível nesta demonstração.', 'aviso');
  });
  container.querySelector('[data-acao="creditos-extra"]').addEventListener('click', function (e) {
    window.PrismaCarregando(e.currentTarget, 'Abrindo…', 700, function () {
      if (window.PrismaToast) window.PrismaToast('Checkout de créditos extras ainda não está disponível nesta demonstração.', 'aviso');
    });
  });
}
