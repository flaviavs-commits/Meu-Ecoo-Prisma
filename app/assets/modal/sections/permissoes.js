/* Secao "Permissões" (workspace, so diretor): matriz somente-leitura de
   cargo x capacidade. Nesta demonstracao os papeis sao fixos - editar
   quem pode o que fica para quando existir backend de verdade. */
const PAPEIS = ['Diretor', 'Coordenador', 'Professor'];
const MATRIZ = [
  { capacidade: 'Gerir créditos de IA', permissoes: [true, true, false] },
  { capacidade: 'Gerir equipe e permissões', permissoes: [true, false, false] },
  { capacidade: 'Ver relatórios da instituição', permissoes: [true, true, false] },
  { capacidade: 'Criar e editar turmas', permissoes: [true, true, false] },
  { capacidade: 'Corrigir avaliações', permissoes: [false, true, true] },
  { capacidade: 'Gerir materiais do acervo', permissoes: [true, true, true] },
  { capacidade: 'Configurar chaves de API', permissoes: [true, false, false] },
];

function marca(pode) {
  return pode
    ? '<svg class="ic" style="color:var(--good)"><use href="#i-check"/></svg>'
    : '<span style="color:var(--ink-3)">—</span>';
}

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Permissões</h2>' +
      '<p>O que cada cargo pode fazer dentro do Prisma.</p>' +
    '</div>' +
    '<div class="tablewrap"><table><thead><tr><th>Capacidade</th>' +
      PAPEIS.map(function (p) { return '<th style="text-align:center">' + p + '</th>'; }).join('') +
    '</tr></thead><tbody>' +
      MATRIZ.map(function (linha) {
        return '<tr><td class="name">' + linha.capacidade + '</td>' +
          linha.permissoes.map(function (p) { return '<td style="text-align:center">' + marca(p) + '</td>'; }).join('') +
        '</tr>';
      }).join('') +
    '</tbody></table></div>' +
    '<p style="font-size:12px;color:var(--ink-3);margin-top:12px">Papéis fixos nesta demonstração — a edição de permissões chega junto com o backend.</p>';
}
