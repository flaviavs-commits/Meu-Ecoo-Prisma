/* Secao "Equipe" (workspace, so diretor): quem tem acesso administrativo
   ou de professor a instituicao, com o cargo de cada um. */
import { avisar } from '../toast.js';
import { confirmar } from '../confirm.js';

const MEMBROS = [
  { id: 'm1', nome: 'Cláudia Nunes', email: 'claudia.nunes@horizonte.edu', papel: 'Diretora', cor: '#C79A2A', eu: true },
  { id: 'm2', nome: 'Ricardo Almeida', email: 'ricardo.almeida@horizonte.edu', papel: 'Professor', cor: '#2C302D' },
  { id: 'm3', nome: 'Fernanda Rocha', email: 'fernanda.rocha@horizonte.edu', papel: 'Coordenadora', cor: '#5b58a8' },
  { id: 'm4', nome: 'Paulo Cezar', email: 'paulo.cezar@horizonte.edu', papel: 'Professor', cor: '#2C302D' },
];

function iniciais(nome) {
  const partes = nome.trim().split(/\s+/);
  return ((partes[0][0] || '') + (partes[partes.length - 1][0] || '')).toUpperCase();
}

function linha(m) {
  return (
    '<div class="rrow" data-id="' + m.id + '">' +
      '<span class="pm-avatar" style="background:' + m.cor + '">' + iniciais(m.nome) + '</span>' +
      '<div class="tx"><b>' + m.nome + (m.eu ? ' <span class="pill p-ia" style="margin-left:6px">você</span>' : '') + '</b><span>' + m.email + '</span></div>' +
      '<div class="end"><span class="pill p-ok">' + m.papel + '</span>' +
      (m.eu ? '' : '<button type="button" class="btn btn-gho btn-sm" data-remover="' + m.id + '">Remover</button>') +
      '</div>' +
    '</div>'
  );
}

export function montar(container, ctx) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Equipe</h2>' +
      '<p>' + MEMBROS.length + ' pessoas com acesso administrativo ou de professor.</p>' +
    '</div>' +
    '<div class="pm-acoes-dir" style="justify-content:flex-start;margin:0 0 6px">' +
      '<button type="button" class="btn btn-pri btn-sm" data-acao="convidar"><svg class="ic"><use href="#i-plus"/></svg><span>Convidar pessoa</span></button>' +
    '</div>' +
    '<div id="pm-equipe-lista">' + MEMBROS.map(linha).join('') + '</div>';

  container.querySelector('[data-acao="convidar"]').addEventListener('click', function () {
    ctx.abrirSecao('convites');
  });

  container.querySelector('#pm-equipe-lista').addEventListener('click', function (e) {
    const btn = e.target.closest('[data-remover]');
    if (!btn) return;
    const linhaEl = btn.closest('.rrow');
    const nome = linhaEl.querySelector('b').childNodes[0].textContent.trim();
    confirmar({
      titulo: 'Remover ' + nome + '?',
      descricao: 'A pessoa perde acesso imediatamente à instituição no Prisma.',
      rotuloConfirmar: 'Remover',
      perigo: true,
      aoConfirmar: function () { return new Promise(function (r) { setTimeout(r, 700); }); },
    }).then(function (ok) {
      if (!ok) return;
      const pai = linhaEl.parentNode;
      const proximo = linhaEl.nextSibling;
      linhaEl.remove();
      if (window.PrismaToastUndo) window.PrismaToastUndo('Pessoa removida da equipe', function () { pai.insertBefore(linhaEl, proximo); });
      avisar('Pessoa removida da equipe', 'ok');
    });
  });
}
