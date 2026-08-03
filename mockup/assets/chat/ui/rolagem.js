/* Scroll inteligente: acompanha o fundo da conversa automaticamente
   enquanto o tutor "digita" - mas para de seguir assim que a pessoa
   rola pra cima por conta propria (ela quer ler algo de novo, nao ser
   arrastada de volta pro fundo a cada chunk do streaming). Uma pilula
   "nova mensagem" aparece nesse caso; clicar nela retoma o seguimento. */
const LIMIAR_COLADO = 88;

/**
 * @param {HTMLElement} elRolagem - o elemento com overflow-y:auto
 * @param {HTMLElement} elHost - onde a pilula flutuante e inserida (position:relative)
 */
export function criarRolagemInteligente(elRolagem, elHost) {
  let seguindo = true;

  const pilula = document.createElement('button');
  pilula.type = 'button';
  pilula.className = 'chat-pilula-nova';
  pilula.innerHTML = '<svg class="ic"><use href="#i-chev"/></svg><span>Nova mensagem</span>';
  pilula.hidden = true;
  elHost.appendChild(pilula);

  function distanciaDoFim() {
    return elRolagem.scrollHeight - elRolagem.scrollTop - elRolagem.clientHeight;
  }

  function irParaOFundo(suave) {
    elRolagem.scrollTo({ top: elRolagem.scrollHeight, behavior: suave ? 'smooth' : 'auto' });
    seguindo = true;
    pilula.hidden = true;
  }

  elRolagem.addEventListener('scroll', function () {
    if (distanciaDoFim() < LIMIAR_COLADO) {
      seguindo = true;
      pilula.hidden = true;
    } else {
      seguindo = false;
    }
  });

  pilula.addEventListener('click', function () { irParaOFundo(true); });

  return {
    /** Chamar sempre que conteudo novo entrar (mensagem nova ou chunk de streaming). */
    aoConteudoMudar: function () {
      if (seguindo) {
        elRolagem.scrollTop = elRolagem.scrollHeight;
      } else {
        pilula.hidden = false;
      }
    },
    irParaOFundo: irParaOFundo,
    estaSeguindo: function () { return seguindo; },
  };
}
