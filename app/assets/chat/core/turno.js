/* Orquestra um "turno" de conversa: mensagem do aluno entra, o tutor
   "pensa" (pausa + indicador), depois "gera" via streaming simulado.
   Unico lugar que sabe a sequencia inteira - composer usa isto para
   enviar, e o botao "regenerar" da mensagem usa a mesma engrenagem
   sem recriar a fala do aluno. */
import { adicionarMensagem, atualizarMensagem } from './loja.js';
import { transmitir } from './streaming.js';
import { gerarResposta } from './respostaIA.js';

let turnoEmAndamento = null;

export function haTurnoEmAndamento() { return !!turnoEmAndamento; }

function executarResposta(idConversa, ganchos) {
  const resposta = gerarResposta();
  const inicio = Date.now();

  const msgIA = adicionarMensagem(idConversa, {
    papel: 'ai',
    texto: '',
    citacoes: resposta.citacoes,
    ferramentas: resposta.ferramentas,
  });

  const controle = transmitir({
    textoFinal: resposta.texto,
    aoAtualizar: function (parcial) {
      ganchos.aoAtualizarTexto(msgIA, parcial);
    },
    aoConcluir: function (info) {
      const tempoMs = Date.now() - inicio;
      atualizarMensagem(idConversa, msgIA.id, {
        texto: info.textoFinal,
        interrompida: info.cancelado,
        tempoRespostaMs: tempoMs,
      });
      turnoEmAndamento = null;
      ganchos.aoConcluir(Object.assign({}, msgIA, { texto: info.textoFinal, interrompida: info.cancelado, tempoRespostaMs: tempoMs }));
    },
  });

  // Marcado ANTES do gancho de UI: o composer consulta `haTurnoEmAndamento()`
  // assim que a mensagem da IA aparece, e precisa ja encontrar `true` -
  // senao o botao "Parar" so aparece um instante depois, fora de sincronia
  // com o que a tela acabou de mostrar.
  turnoEmAndamento = { idConversa: idConversa, cancelar: controle.cancelar };
  ganchos.aoCriarMensagemIA(msgIA);
}

/**
 * @param {string} idConversa
 * @param {string} textoUsuario
 * @param {Array} anexos
 * @param {{aoCriarMensagemUsuario, aoIniciarResposta, aoCriarMensagemIA, aoAtualizarTexto, aoConcluir}} ganchos
 */
export function enviarTurno(idConversa, textoUsuario, anexos, ganchos) {
  const msgUsuario = adicionarMensagem(idConversa, { papel: 'user', texto: textoUsuario, anexos: anexos || [] });
  ganchos.aoCriarMensagemUsuario(msgUsuario);

  setTimeout(function () {
    ganchos.aoIniciarResposta();
    setTimeout(function () { executarResposta(idConversa, ganchos); }, 550 + Math.random() * 500);
  }, 120);
}

/** Regenerar: nao cria fala nova do aluno, so um novo turno de resposta. */
export function regenerarTurno(idConversa, ganchos) {
  ganchos.aoIniciarResposta();
  setTimeout(function () { executarResposta(idConversa, ganchos); }, 400 + Math.random() * 400);
}

export function cancelarTurno() {
  if (turnoEmAndamento) turnoEmAndamento.cancelar();
}
