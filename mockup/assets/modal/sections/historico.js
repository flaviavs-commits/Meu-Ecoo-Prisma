/* Secao "Histórico" (workspace, so diretor): linha do tempo de acoes
   relevantes na conta - mais legivel que os Logs, que sao para
   auditoria tecnica. */
const EVENTOS = [
  { icone: 'i-user', titulo: 'Perfil atualizado', quando: 'hoje, 09:14' },
  { icone: 'i-key', titulo: 'Chave de API "Backup noturno" criada', quando: 'ontem, 22:03' },
  { icone: 'i-plus', titulo: 'Convite enviado para juliana.matos@horizonte.edu', quando: '2 dias atrás' },
  { icone: 'i-coin', titulo: 'Plano renovado — Institucional Plus', quando: '12 de julho' },
  { icone: 'i-shield', titulo: 'Senha alterada', quando: '28 de junho' },
  { icone: 'i-users', titulo: 'Fernanda Rocha adicionada à equipe', quando: '15 de junho' },
];

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Histórico</h2>' +
      '<p>Ações recentes realizadas nesta conta.</p>' +
    '</div>' +
    EVENTOS.map(function (ev) {
      return (
        '<div class="rrow">' +
          '<span class="mic"><svg class="ic"><use href="#' + ev.icone + '"/></svg></span>' +
          '<div class="tx"><b>' + ev.titulo + '</b></div>' +
          '<span style="margin-left:auto;font-size:11.5px;color:var(--ink-3);white-space:nowrap">' + ev.quando + '</span>' +
        '</div>'
      );
    }).join('');
}
