/* Secao "Ajuda": busca (filtra as perguntas frequentes na hora) +
   contato. Sem backend real, entao "buscar" e um filtro de texto sobre
   uma lista fixa - ainda assim precisa parecer de verdade, com estado
   vazio quando nada bate. */
const PERGUNTAS = [
  { p: 'Como o tutor de IA escolhe as questões?', r: 'Ele parte do seu histórico de acertos e erros nos simulados e prioriza os tópicos onde você mais precisa de prática.' },
  { p: 'Os créditos de IA expiram?', r: 'Não. Créditos não usados no mês seguem disponíveis enquanto a instituição mantiver o plano ativo.' },
  { p: 'Posso trocar de turma?', r: 'Só quem administra a instituição pode mover alunos entre turmas - fale com a coordenação.' },
  { p: 'Como funciona a correção automática?', r: 'A IA sugere uma nota e um comentário; o professor sempre revisa antes de publicar - nenhuma nota sai sem revisão humana.' },
  { p: 'Meus dados são usados para treinar modelos de IA?', r: 'Não. As chamadas passam por um gateway que não reaproveita conteúdo de alunos para treino.' },
];

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Pessoal</p>' +
      '<h2>Ajuda</h2>' +
      '<p>Perguntas frequentes e como falar com a gente.</p>' +
    '</div>' +
    '<div class="pm-busca"><svg class="ic"><use href="#i-search"/></svg><input type="text" id="pm-ajuda-busca" placeholder="Buscar em perguntas frequentes…"></div>' +
    '<div class="pm-faq" id="pm-ajuda-faq"></div>' +
    '<div class="pm-vazio" id="pm-ajuda-vazio" style="display:none">' +
      '<span class="pm-vazio-ic"><svg class="ic"><use href="#i-search"/></svg></span>' +
      '<b>Nada encontrado</b><span>Tente outra palavra ou fale direto com o suporte abaixo.</span>' +
    '</div>' +
    '<div class="pm-sep"></div>' +
    '<div class="pm-perigo" style="border-color:var(--line);background:var(--card2)">' +
      '<div class="pm-perigo-linha">' +
        '<div><b>Falar com o suporte</b><span>Resposta em até 1 dia útil.</span></div>' +
        '<button type="button" class="btn btn-gho btn-sm" data-acao="contato"><svg class="ic"><use href="#i-mail"/></svg><span>Contatar</span></button>' +
      '</div>' +
    '</div>';

  const faqEl = container.querySelector('#pm-ajuda-faq');
  const vazioEl = container.querySelector('#pm-ajuda-vazio');

  function renderizar(filtro) {
    const q = (filtro || '').trim().toLowerCase();
    const visiveis = PERGUNTAS.filter(function (item) {
      return !q || item.p.toLowerCase().indexOf(q) !== -1 || item.r.toLowerCase().indexOf(q) !== -1;
    });
    faqEl.style.display = visiveis.length ? '' : 'none';
    vazioEl.style.display = visiveis.length ? 'none' : 'flex';
    faqEl.innerHTML = visiveis.map(function (item) {
      return '<details><summary>' + item.p + '</summary><div class="pm-faq-r">' + item.r + '</div></details>';
    }).join('');
  }
  renderizar('');

  container.querySelector('#pm-ajuda-busca').addEventListener('input', function (e) { renderizar(e.target.value); });

  container.querySelector('[data-acao="contato"]').addEventListener('click', function () {
    if (window.PrismaToast) window.PrismaToast('Em breve: canal direto de suporte.', 'aviso');
  });
}
