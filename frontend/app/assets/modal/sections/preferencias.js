/* Secao "Preferências": tema e idioma. Nao reinventa nenhum dos dois -
   so oferece um lugar central para eles, chamando o mesmo motor que a
   topbar ja usa (`window.PrismaTheme`, `window.PrismaI18n`), para o
   estado nunca divergir entre os dois lugares que o controlam. */
const IDIOMAS = [
  { codigo: 'pt-BR', nome: 'Português', regiao: 'Brasil' },
  { codigo: 'en', nome: 'English', regiao: 'United States' },
  { codigo: 'es', nome: 'Español', regiao: 'España' },
  { codigo: 'fr', nome: 'Français', regiao: 'France' },
  { codigo: 'de', nome: 'Deutsch', regiao: 'Deutschland' },
];

export function montar(container) {
  const temaAtual = window.PrismaTheme ? window.PrismaTheme.atual() : 'light';
  const idiomaAtual = window.PrismaI18n ? window.PrismaI18n.idiomaAtual() : 'pt-BR';

  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Pessoal</p>' +
      '<h2>Preferências</h2>' +
      '<p>Aparência e idioma da interface.</p>' +
    '</div>' +

    '<h3 class="pm-subtitulo">Tema</h3>' +
    '<div class="pm-segmentado" role="radiogroup" aria-label="Tema" id="pm-pref-tema">' +
      '<button type="button" data-tema="light" role="radio"><svg class="ic"><use href="#i-sun"/></svg><span>Claro</span></button>' +
      '<button type="button" data-tema="dark" role="radio"><svg class="ic"><use href="#i-moon"/></svg><span>Escuro</span></button>' +
    '</div>' +

    '<div class="pm-sep"></div>' +
    '<h3 class="pm-subtitulo">Idioma</h3>' +
    '<ul class="list" id="pm-pref-idiomas">' +
      IDIOMAS.map(function (l) {
        return (
          '<li data-ir data-idioma="' + l.codigo + '">' +
            '<span class="dot" style="--c:var(--green)"></span>' +
            '<div class="tx"><b>' + l.nome + '</b><span>' + l.regiao + '</span></div>' +
            '<span class="pill p-ok pm-pref-atual" style="' + (l.codigo === idiomaAtual ? '' : 'display:none') + '">Atual</span>' +
          '</li>'
        );
      }).join('') +
    '</ul>';

  const btnsTema = container.querySelectorAll('#pm-pref-tema button');
  function pintarTema(t) {
    btnsTema.forEach(function (b) {
      const on = b.dataset.tema === t;
      b.classList.toggle('on', on);
      b.setAttribute('aria-checked', String(on));
    });
  }
  pintarTema(temaAtual);
  btnsTema.forEach(function (b) {
    b.addEventListener('click', function () {
      if (window.PrismaTheme) window.PrismaTheme.aplicar(b.dataset.tema);
      pintarTema(b.dataset.tema);
    });
  });

  container.querySelector('#pm-pref-idiomas').addEventListener('click', function (e) {
    const li = e.target.closest('[data-idioma]');
    if (!li || !window.PrismaI18n) return;
    window.PrismaI18n.setLang(li.dataset.idioma);
    container.querySelectorAll('#pm-pref-idiomas .pm-pref-atual').forEach(function (pill) {
      pill.style.display = pill.closest('li') === li ? '' : 'none';
    });
  });
}
