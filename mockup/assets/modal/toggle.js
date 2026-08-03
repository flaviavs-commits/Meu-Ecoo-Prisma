/* Liga o comportamento dos botoes `.tg` (role="switch") criados dentro
   de uma secao do settings. O `.tg` generico de app.js so varre a
   pagina uma vez, no carregamento - conteudo criado depois (como as
   secoes deste modal, montadas sob demanda) precisa da mesma logica
   aplicada de novo, so no proprio container. */
export function ligarToggles(container) {
  container.querySelectorAll('.tg').forEach(function (t) {
    t.addEventListener('click', function () {
      const ligado = t.classList.toggle('off') === false;
      t.setAttribute('aria-checked', String(ligado));
    });
  });
}
