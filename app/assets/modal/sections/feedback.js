/* Secao "Feedback": avaliacao por estrelas + categoria + mensagem.
   Envio troca o formulario inteiro por uma tela de agradecimento em vez
   de empilhar um banner - o formulario ja cumpriu seu papel. */
export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Pessoal</p>' +
      '<h2>Feedback</h2>' +
      '<p>O que está funcionando bem e o que ainda incomoda.</p>' +
    '</div>' +
    '<div id="pm-fb-form">' +
      '<div class="field"><label>Como está sua experiência com o Prisma?</label>' +
        '<div class="pm-estrelas" id="pm-fb-estrelas" role="radiogroup" aria-label="Avaliação de 1 a 5">' +
          [1, 2, 3, 4, 5].map(function (n) {
            return '<button type="button" data-nota="' + n + '" aria-label="' + n + ' de 5"><svg class="ic"><use href="#i-star"/></svg></button>';
          }).join('') +
        '</div>' +
      '</div>' +
      '<div class="field"><label>Categoria</label>' +
        '<select class="input" id="pm-fb-categoria">' +
          '<option value="ideia">Sugestão</option>' +
          '<option value="bug">Problema técnico</option>' +
          '<option value="elogio">Elogio</option>' +
          '<option value="outro">Outro</option>' +
        '</select>' +
      '</div>' +
      '<div class="field"><label>Mensagem</label><textarea class="input" id="pm-fb-msg" rows="4" style="resize:vertical" placeholder="Conte com detalhes…"></textarea></div>' +
      '<div class="pm-acoes-dir"><button type="button" class="btn btn-pri" data-acao="enviar">Enviar feedback</button></div>' +
    '</div>';

  let nota = 0;
  const estrelas = container.querySelectorAll('#pm-fb-estrelas button');
  estrelas.forEach(function (btn) {
    btn.addEventListener('click', function () {
      nota = Number(btn.dataset.nota);
      estrelas.forEach(function (b) { b.classList.toggle('on', Number(b.dataset.nota) <= nota); });
    });
  });

  container.querySelector('[data-acao="enviar"]').addEventListener('click', function (e) {
    const msg = container.querySelector('#pm-fb-msg').value.trim();
    const btn = e.currentTarget;
    if (!msg) {
      container.querySelector('#pm-fb-msg').focus();
      return;
    }
    window.PrismaCarregando(btn, 'Enviando…', 900, function () {
      container.querySelector('#pm-fb-form').innerHTML =
        '<div class="pm-sucesso-full">' +
          '<span class="pm-sucesso-ic"><svg class="ic"><use href="#i-check"/></svg></span>' +
          '<h4>Obrigado pelo feedback!</h4>' +
          '<p>Sua mensagem chegou até a equipe do Prisma e ajuda a priorizar o que vem a seguir.</p>' +
        '</div>';
    });
  });
}
