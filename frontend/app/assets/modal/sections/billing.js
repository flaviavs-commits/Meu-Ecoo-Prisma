/* Secao "Faturamento" (workspace, so diretor): metodo de pagamento e
   historico de faturas da instituicao. */
import { avisar } from '../toast.js';

const FATURAS = [
  { id: 'f1', ref: 'Agosto 2026', valor: 'R$ 1.890,00', status: 'ok', rotulo: 'Paga' },
  { id: 'f2', ref: 'Julho 2026', valor: 'R$ 1.890,00', status: 'ok', rotulo: 'Paga' },
  { id: 'f3', ref: 'Junho 2026', valor: 'R$ 1.890,00', status: 'ok', rotulo: 'Paga' },
];

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Faturamento</h2>' +
      '<p>Método de pagamento e faturas emitidas para a instituição.</p>' +
    '</div>' +
    '<h3 class="pm-subtitulo">Método de pagamento</h3>' +
    '<div class="pm-cartao">' +
      '<span class="pm-cartao-ic">VISA</span>' +
      '<div><b>•••• •••• •••• 4242</b><span>expira em 08/29</span></div>' +
      '<button type="button" class="btn btn-gho btn-sm" style="margin-left:auto" data-acao="trocar-cartao">Trocar</button>' +
    '</div>' +
    '<div class="pm-sep"></div>' +
    '<h3 class="pm-subtitulo">Faturas</h3>' +
    '<div class="tablewrap"><table><thead><tr><th>Referência</th><th>Valor</th><th>Status</th><th></th></tr></thead><tbody>' +
      FATURAS.map(function (f) {
        return (
          '<tr><td class="name">' + f.ref + '</td><td>' + f.valor + '</td>' +
          '<td><span class="pill p-' + f.status + '">' + f.rotulo + '</span></td>' +
          '<td style="text-align:right"><button type="button" class="pm-key-ico-btn" data-baixar="' + f.id + '" aria-label="Baixar fatura"><svg class="ic"><use href="#i-download"/></svg></button></td></tr>'
        );
      }).join('') +
    '</tbody></table></div>';

  container.querySelector('[data-acao="trocar-cartao"]').addEventListener('click', function () {
    avisar('Troca de cartão ainda não está disponível nesta demonstração.', 'aviso');
  });
  container.querySelectorAll('[data-baixar]').forEach(function (btn) {
    btn.addEventListener('click', function () { avisar('Fatura baixada (simulação)', 'ok'); });
  });
}
