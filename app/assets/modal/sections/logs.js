/* Secao "Logs" (workspace, so diretor): auditoria tecnica - quem fez o
   que, de onde. Mais denso e monoespacado que o Histórico de proposito:
   publico diferente (auditoria/segurança, nao "o que eu fiz"). */
const REGISTROS = [
  { quando: '2026-08-03 09:14:02', ator: 'claudia.nunes', acao: 'auth.login', ip: '187.4.22.10' },
  { quando: '2026-08-02 22:03:41', ator: 'claudia.nunes', acao: 'apikey.create', ip: '187.4.22.10' },
  { quando: '2026-08-01 14:52:18', ator: 'ricardo.almeida', acao: 'grade.publish', ip: '201.9.13.87' },
  { quando: '2026-07-30 08:11:56', ator: 'sistema', acao: 'billing.charge.success', ip: '—' },
  { quando: '2026-07-28 17:40:03', ator: 'claudia.nunes', acao: 'team.invite.sent', ip: '187.4.22.10' },
  { quando: '2026-06-28 11:22:47', ator: 'claudia.nunes', acao: 'auth.password.changed', ip: '187.4.22.10' },
];

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Logs</h2>' +
      '<p>Registro técnico de ações na conta, para auditoria.</p>' +
    '</div>' +
    '<div class="pm-busca"><svg class="ic"><use href="#i-search"/></svg><input type="text" id="pm-logs-busca" placeholder="Filtrar por ação ou pessoa…"></div>' +
    '<div id="pm-logs-lista"></div>' +
    '<div class="pm-vazio" id="pm-logs-vazio" style="display:none">' +
      '<span class="pm-vazio-ic"><svg class="ic"><use href="#i-doc"/></svg></span>' +
      '<b>Nenhum registro encontrado</b><span>Ajuste o filtro para ver mais eventos.</span>' +
    '</div>';

  const listaEl = container.querySelector('#pm-logs-lista');
  const vazioEl = container.querySelector('#pm-logs-vazio');

  function renderizar(filtro) {
    const q = (filtro || '').trim().toLowerCase();
    const visiveis = REGISTROS.filter(function (r) {
      return !q || r.acao.toLowerCase().indexOf(q) !== -1 || r.ator.toLowerCase().indexOf(q) !== -1;
    });
    listaEl.style.display = visiveis.length ? '' : 'none';
    vazioEl.style.display = visiveis.length ? 'none' : 'flex';
    listaEl.innerHTML = visiveis.map(function (r) {
      return (
        '<div class="pm-log-linha">' +
          '<span class="pm-log-quando">' + r.quando + '</span>' +
          '<span class="pm-log-txt"><b>' + r.acao + '</b> <span>· ' + r.ator + '</span></span>' +
          '<span class="pm-log-ip">' + r.ip + '</span>' +
        '</div>'
      );
    }).join('');
  }
  renderizar('');

  container.querySelector('#pm-logs-busca').addEventListener('input', function (e) { renderizar(e.target.value); });
}
