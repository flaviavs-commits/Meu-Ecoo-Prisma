/* Contagem de tokens aproximada - sem gateway de IA neste repositorio,
   nao ha tokenizer real do modelo disponivel. Usa a heuristica comum
   (~4 caracteres por token em portugues/ingles), a mesma ordem de
   grandeza que provedores documentam para estimativa rapida. Nunca
   apresentar como valor exato - so como aproximacao, visivel na UI
   com um "~". */
export function contarTokens(texto) {
  if (!texto) return 0;
  return Math.max(1, Math.round(texto.length / 4));
}

export function contarTokensConversa(conversa) {
  return conversa.mensagens.reduce(function (soma, m) { return soma + contarTokens(m.texto); }, 0);
}
