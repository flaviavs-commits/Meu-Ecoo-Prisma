/* Secao "Notificações": preferencias de aviso, agrupadas por canal. */
import { ligarToggles } from '../toggle.js';

const GRUPOS = [
  {
    rotulo: 'Produto',
    itens: [
      { id: 'lembretes', titulo: 'Lembretes de estudo', desc: 'sugestões diárias do tutor', ligado: true },
      { id: 'novidades', titulo: 'Novidades do Prisma', desc: 'recursos novos e melhorias', ligado: true },
    ],
  },
  {
    rotulo: 'E-mail',
    itens: [
      { id: 'resumo', titulo: 'Resumo semanal', desc: 'desempenho e progresso da semana', ligado: false },
      { id: 'seguranca-email', titulo: 'Alertas de segurança', desc: 'login em novo dispositivo', ligado: true },
    ],
  },
];

function linha(item) {
  return (
    '<div class="togglerow" data-item="' + item.id + '">' +
      '<span><span>' + item.titulo + '</span><small>' + item.desc + '</small></span>' +
      '<button type="button" class="tg' + (item.ligado ? '' : ' off') + '" role="switch" aria-checked="' + item.ligado + '" aria-label="' + item.titulo + '"></button>' +
    '</div>'
  );
}

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Pessoal</p>' +
      '<h2>Notificações</h2>' +
      '<p>Escolha o que vale a pena interromper você.</p>' +
    '</div>' +
    GRUPOS.map(function (g) {
      return '<h3 class="pm-subtitulo">' + g.rotulo + '</h3><div style="margin-bottom:8px">' + g.itens.map(linha).join('') + '</div>';
    }).join('');

  ligarToggles(container);
}
