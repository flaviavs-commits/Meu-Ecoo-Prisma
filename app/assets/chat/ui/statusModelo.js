/* Pilula de status na barra do tutor: qual "classe de modelo" esta
   servindo a sessao e se esta ocupado - a mesma ideia de roteamento
   multi-modelo do OpenRouter (ver IA.md), so que aqui e so a
   apresentacao, sem gateway de verdade por tras. */
const MODELOS = ['roteamento automático', 'classe: raciocínio', 'classe: rápida'];

export function montarStatusModelo(container) {
  container.innerHTML =
    '<span class="chat-status-dot"></span>' +
    '<span class="chat-status-tx">Prisma Tutor · <b data-status-modelo>' + MODELOS[0] + '</b></span>';
  const dot = container.querySelector('.chat-status-dot');
  const tx = container.querySelector('[data-status-modelo]');

  return {
    definirOcupado: function (ocupado) {
      dot.classList.toggle('ocupado', ocupado);
      tx.textContent = ocupado ? 'selecionando o melhor modelo…' : MODELOS[Math.floor(Math.random() * MODELOS.length)];
    },
  };
}
