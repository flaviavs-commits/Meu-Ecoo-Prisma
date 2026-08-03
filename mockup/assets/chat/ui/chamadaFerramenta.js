/* Cartao de "chamada de ferramenta" - o tutor mostrando de onde tirou
   a resposta (um arquivo de contexto, um flashcard, uma busca) antes
   do texto propriamente dito. Mesmo padrao visual do Cursor/Claude
   quando exibem uma tool call: rotulo + estado + icone. */
export function renderizarFerramentas(ferramentas) {
  if (!ferramentas || !ferramentas.length) return '';
  return (
    '<div class="chat-ferramentas">' +
    ferramentas.map(function (f) {
      const concluida = f.status === 'concluida';
      return (
        '<div class="chat-ferramenta' + (concluida ? ' concluida' : '') + '">' +
          '<span class="chat-ferramenta-ic">' +
            (concluida
              ? '<svg class="ic"><use href="#i-check"/></svg>'
              : '<span class="tut-file-spin"></span>') +
          '</span>' +
          '<span class="chat-ferramenta-tx">' +
            '<b>' + (concluida ? 'Consultou' : 'Consultando') + '</b> ' + f.nome +
          '</span>' +
        '</div>'
      );
    }).join('') +
    '</div>'
  );
}
