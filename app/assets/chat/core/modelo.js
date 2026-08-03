/* Fabrica dos tres formatos de dado do chat (mensagem, conversa,
   pasta) - um lugar so gerando id e timestamp, para nunca duas partes
   do codigo inventarem id de jeitos diferentes e colidirem. */
let seq = 0;
function idUnico(prefixo) {
  seq += 1;
  return prefixo + '_' + Date.now().toString(36) + '_' + seq.toString(36);
}

/**
 * @param {{papel:'user'|'ai', texto:string, anexos?:Array, citacoes?:Array,
 *   ferramentas?:Array, tipo?:'texto'|'quiz', opcoes?:Array<string>,
 *   corretaIndice?:number, respondidoIndice?:number, tempoRespostaMs?:number}} dados
 */
export function criarMensagem(dados) {
  return {
    id: idUnico('m'),
    papel: dados.papel,
    texto: dados.texto || '',
    anexos: dados.anexos || [],
    citacoes: dados.citacoes || [],
    ferramentas: dados.ferramentas || [],
    tipo: dados.tipo || 'texto',
    opcoes: dados.opcoes || null,
    corretaIndice: dados.corretaIndice !== undefined ? dados.corretaIndice : null,
    respondidoIndice: dados.respondidoIndice !== undefined ? dados.respondidoIndice : null,
    fixada: false,
    editada: false,
    interrompida: false,
    criadaEm: Date.now(),
    tempoRespostaMs: dados.tempoRespostaMs !== undefined ? dados.tempoRespostaMs : (dados.papel === 'ai' ? null : undefined),
    tokens: null,
  };
}

/**
 * @param {{titulo:string, materiaId:string, mensagens?:Array}} dados
 */
export function criarConversa(dados) {
  const agora = Date.now();
  return {
    id: idUnico('c'),
    titulo: dados.titulo || 'Nova conversa',
    materiaId: dados.materiaId || 'geral',
    pastaId: dados.pastaId || null,
    tags: dados.tags || [],
    favorita: false,
    criadaEm: agora,
    atualizadaEm: agora,
    mensagens: dados.mensagens || [],
  };
}

export function criarPasta(nome) {
  return { id: idUnico('p'), nome: nome };
}
