/* Fabrica das acoes que cada mensagem expoe (copiar, editar, regenerar,
   fixar, compartilhar, responder quiz). Fica separado de `index.js`
   para o arquivo de boot nao acumular a logica de cada botao - aqui so
   traduz clique em chamada de loja/turno/compartilhar. */
import * as loja from './loja.js';
import { regenerarTurno, enviarTurno } from './turno.js';
import { avisar } from '../../modal/toast.js';
import { abrirCompartilhar } from '../ui/compartilhar.js';

/**
 * @param {{
 *   idConversaAtual: () => string,
 *   rerenderizarConversa: () => void,
 *   ganchosTurno: object,
 * }} deps
 */
export function criarAcoesMensagem(deps) {
  return {
    copiar: function () { avisar('Mensagem copiada', 'ok'); },

    editarSalvar: function (msg, novoTexto) {
      const idConversa = deps.idConversaAtual();
      loja.truncarApartirDe(idConversa, msg.id);
      deps.rerenderizarConversa();
      enviarTurno(idConversa, novoTexto, msg.anexos, deps.ganchosTurno);
    },

    regenerar: function (msg) {
      const idConversa = deps.idConversaAtual();
      loja.truncarApartirDe(idConversa, msg.id);
      deps.rerenderizarConversa();
      regenerarTurno(idConversa, deps.ganchosTurno);
    },

    fixar: function (msg, fixada) {
      loja.fixarMensagem(deps.idConversaAtual(), msg.id, fixada);
      avisar(fixada ? 'Mensagem fixada' : 'Mensagem desafixada', 'ok');
    },

    compartilhar: function (msg) {
      const c = loja.obterConversa(deps.idConversaAtual());
      abrirCompartilhar({ titulo: c ? c.titulo : 'Conversa', idConversa: c ? c.id : '', texto: msg.texto });
    },

    responderQuiz: function (msg, indice) {
      loja.atualizarMensagem(deps.idConversaAtual(), msg.id, { respondidoIndice: indice });
      deps.rerenderizarConversa();
    },
  };
}
