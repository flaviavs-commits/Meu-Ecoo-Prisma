/* Simulador de streaming: nao ha IA de verdade por tras (gateway ainda
   nao existe neste repositorio), entao a resposta completa ja existe
   de antemao - o que este modulo faz e REVELA-LA aos poucos, em
   pedacos de tamanho variavel e com pausa maior depois de pontuacao,
   para parecer geracao real em vez de um texto colado. Cancelavel a
   qualquer momento (botao "Parar" ou Esc). */

function partirEmPedacos(texto) {
  // Mantem espacos/quebras de linha como parte do pedaco anterior, para
  // o texto parcial nunca ficar com espacamento errado no meio do render.
  const partes = texto.match(/\S+\s*/g) || [];
  const pedacos = [];
  let acumulado = '';
  partes.forEach(function (parte, i) {
    acumulado += parte;
    // Agrupa de 1 a 3 palavras por pedaco - streaming real nao revela
    // palavra por palavra, revela em rajadas curtas.
    if (i % 2 === 1 || i === partes.length - 1) {
      pedacos.push(acumulado);
      acumulado = '';
    }
  });
  if (acumulado) pedacos.push(acumulado);
  return pedacos;
}

/**
 * @param {{
 *   textoFinal: string,
 *   aoAtualizar: (textoParcial: string, concluido: boolean) => void,
 *   aoConcluir: (info: {cancelado: boolean, textoFinal: string}) => void,
 * }} opcoes
 * @returns {{cancelar: () => void}}
 */
export function transmitir(opcoes) {
  const pedacos = partirEmPedacos(opcoes.textoFinal);
  let indice = 0;
  let acumulado = '';
  let cancelado = false;
  let timer = null;

  function atraso(pedaco) {
    const base = 14 + Math.random() * 26;
    // Pausa maior apos frase/paragrafo: imita a cadencia de um modelo
    // "pensando" na proxima ideia, nao so digitando.
    if (/[.!?]\s*$/.test(pedaco)) return base + 160;
    if (/\n\n$/.test(pedaco)) return base + 220;
    return base;
  }

  function passo() {
    if (cancelado) return;
    if (indice >= pedacos.length) {
      opcoes.aoAtualizar(acumulado, true);
      opcoes.aoConcluir({ cancelado: false, textoFinal: acumulado });
      return;
    }
    acumulado += pedacos[indice];
    opcoes.aoAtualizar(acumulado, false);
    const pedacoAtual = pedacos[indice];
    indice += 1;
    timer = setTimeout(passo, atraso(pedacoAtual));
  }

  timer = setTimeout(passo, 120); // pausa inicial - "pensando" antes do primeiro token

  return {
    cancelar: function () {
      if (cancelado) return;
      cancelado = true;
      if (timer) clearTimeout(timer);
      opcoes.aoConcluir({ cancelado: true, textoFinal: acumulado });
    },
  };
}
