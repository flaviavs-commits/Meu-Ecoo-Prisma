/* Rodape de citacoes de uma mensagem (a lista numerada no fim da
   bolha) e o popover que abre ao clicar num marcador `[1]` inline -
   o markdown so cria o marcador, este modulo cuida do resto. */

export function renderizarRodapeCitacoes(citacoes) {
  if (!citacoes || !citacoes.length) return '';
  return (
    '<ol class="chat-citas-rodape">' +
    citacoes.map(function (c) {
      return '<li><b>[' + c.numero + ']</b> <span>' + c.fonte + '</span>' +
        (c.trecho ? '<small>' + c.trecho + '</small>' : '') + '</li>';
    }).join('') +
    '</ol>'
  );
}

/** Liga o clique/teclado nos marcadores `[n]` dentro de um container ja renderizado. */
export function ligarCitacoesInline(container, citacoes) {
  if (!citacoes || !citacoes.length) return;
  const porNumero = {};
  citacoes.forEach(function (c) { porNumero[c.numero] = c; });

  container.querySelectorAll('.chat-cita').forEach(function (marcador) {
    if (marcador.dataset.ligado) return;
    marcador.dataset.ligado = '1';

    function alternar() {
      const aberto = marcador.classList.toggle('aberto');
      let pop = marcador.querySelector('.chat-cita-pop');
      if (aberto) {
        if (!pop) {
          const c = porNumero[marcador.dataset.cita];
          if (!c) return;
          pop = document.createElement('span');
          pop.className = 'chat-cita-pop';
          pop.innerHTML = '<b>' + c.fonte + '</b>' + (c.trecho ? '<small>' + c.trecho + '</small>' : '');
          marcador.appendChild(pop);
        }
      } else if (pop) {
        pop.remove();
      }
    }

    marcador.addEventListener('click', function (e) { e.stopPropagation(); alternar(); });
    marcador.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); alternar(); }
    });
  });

  // Clicar fora fecha qualquer popover aberto neste container.
  if (!container.dataset.citasFechamGlobal) {
    container.dataset.citasFechamGlobal = '1';
    document.addEventListener('click', function () {
      container.querySelectorAll('.chat-cita.aberto').forEach(function (m) {
        m.classList.remove('aberto');
        const pop = m.querySelector('.chat-cita-pop');
        if (pop) pop.remove();
      });
    });
  }
}
