/* Renderiza uma mensagem (aluno ou tutor) e liga as acoes por cima
   dela: copiar, editar, regenerar, fixar, compartilhar, e a interacao
   do cartao de quiz. E o unico modulo que sabe montar o DOM de uma
   mensagem - streaming, sidebar e busca so leem o modelo, quem
   desenha a bolha e sempre este arquivo. */
import { renderizarMarkdown } from '../core/markdown.js';
import { contarTokens } from '../core/tokens.js';
import { ligarBlocosDeCodigo } from './blocoCodigo.js';
import { renderizarRodapeCitacoes, ligarCitacoesInline } from './citacoes.js';
import { renderizarFerramentas } from './chamadaFerramenta.js';

const AV_TUTOR = '<span class="tmsg-av"><svg><use href="#i-spark"/></svg></span>';

function tempoRelativo(ms) {
  if (ms == null) return '';
  return ms < 1000 ? ms + ' ms' : (ms / 1000).toFixed(1).replace('.', ',') + ' s';
}

function renderizarConteudoBolha(msg) {
  if (msg.tipo === 'quiz') return renderizarQuiz(msg);
  const markdown = renderizarMarkdown(msg.texto, { citacoes: msg.citacoes });
  return markdown + renderizarRodapeCitacoes(msg.citacoes);
}

function renderizarQuiz(msg) {
  const letras = ['a', 'b', 'c', 'd', 'e', 'f'];
  const respondido = msg.respondidoIndice !== null;
  return (
    '<div class="tmsg-quiz">' +
      '<span class="tmsg-tag">Questão</span>' +
      '<p>' + renderizarMarkdown(msg.texto, { citacoes: msg.citacoes }).replace(/^<p>|<\/p>$/g, '') + '</p>' +
      '<div class="tut-opts' + (respondido ? ' respondido' : '') + '">' +
        msg.opcoes.map(function (op, i) {
          let classe = '';
          if (respondido) {
            if (i === msg.corretaIndice) classe = ' certa';
            else if (i === msg.respondidoIndice) classe = ' errada';
          }
          return '<button class="tut-opt' + classe + '" data-indice="' + i + '"' + (respondido ? ' disabled' : '') + '><b>' + letras[i] + '</b>' + op + '</button>';
        }).join('') +
      '</div>' +
      renderizarRodapeCitacoes(msg.citacoes) +
    '</div>'
  );
}

function renderizarAnexos(anexos) {
  if (!anexos || !anexos.length) return '';
  return (
    '<div class="chat-anexos-msg">' +
    anexos.map(function (a) {
      return '<span class="chat-anexo-chip"><svg class="ic"><use href="#i-doc"/></svg>' + a.nome + '</span>';
    }).join('') +
    '</div>'
  );
}

function renderizarAcoes(msg) {
  const podeEditar = msg.papel === 'user';
  const podeRegenerar = msg.papel === 'ai' && msg.tipo !== 'quiz';
  return (
    '<div class="tmsg-acoes">' +
      '<button type="button" class="tmsg-acao" data-acao="copiar" aria-label="Copiar"><svg class="ic"><use href="#i-copy"/></svg></button>' +
      (podeEditar ? '<button type="button" class="tmsg-acao" data-acao="editar" aria-label="Editar"><svg class="ic"><use href="#i-edit"/></svg></button>' : '') +
      (podeRegenerar ? '<button type="button" class="tmsg-acao" data-acao="regenerar" aria-label="Regenerar"><svg class="ic"><use href="#i-refresh"/></svg></button>' : '') +
      '<button type="button" class="tmsg-acao' + (msg.fixada ? ' on' : '') + '" data-acao="fixar" aria-label="Fixar" aria-pressed="' + msg.fixada + '"><svg class="ic"><use href="#i-pin"/></svg></button>' +
      '<button type="button" class="tmsg-acao" data-acao="compartilhar" aria-label="Compartilhar"><svg class="ic"><use href="#i-share"/></svg></button>' +
    '</div>'
  );
}

function renderizarMeta(msg) {
  if (msg.papel !== 'ai' || msg.tipo === 'quiz') return '';
  const partes = [];
  if (msg.tempoRespostaMs != null) partes.push(tempoRelativo(msg.tempoRespostaMs));
  partes.push('~' + contarTokens(msg.texto) + ' tokens');
  if (msg.interrompida) partes.push('interrompida');
  if (msg.editada) partes.push('editada');
  return '<div class="tmsg-meta">' + partes.join(' · ') + '</div>';
}

/**
 * @param {object} msg
 * @param {{
 *   copiar:(msg)=>void, editarSalvar:(msg,novoTexto)=>void, regenerar:(msg)=>void,
 *   fixar:(msg,fixada)=>void, compartilhar:(msg)=>void, responderQuiz:(msg,indice)=>void,
 * }} acoes
 */
export function montarMensagem(msg, acoes) {
  const el = document.createElement('div');
  el.className = 'tmsg ' + (msg.papel === 'ai' ? 'ai' : 'me');
  el.dataset.id = msg.id;

  el.innerHTML =
    (msg.papel === 'ai' ? AV_TUTOR : '') +
    '<div class="tmsg-col">' +
      renderizarFerramentas(msg.ferramentas) +
      '<div class="tmsg-bubble' + (msg.tipo === 'quiz' ? ' tmsg-quiz-host' : '') + '">' + renderizarConteudoBolha(msg) + '</div>' +
      renderizarAnexos(msg.anexos) +
      renderizarMeta(msg) +
      renderizarAcoes(msg) +
    '</div>';

  const bolha = el.querySelector('.tmsg-bubble');
  ligarBlocosDeCodigo(bolha);
  ligarCitacoesInline(bolha, msg.citacoes);
  ligarAcoes(el, msg, acoes);
  if (msg.tipo === 'quiz') ligarQuiz(el, msg, acoes);

  return el;
}

/** Re-renderiza so o conteudo da bolha - usado a cada chunk do streaming, sem recriar a mensagem inteira. */
export function atualizarBolhaStreaming(el, textoParcial, citacoes) {
  const bolha = el.querySelector('.tmsg-bubble');
  bolha.innerHTML = renderizarMarkdown(textoParcial, { citacoes: citacoes });
  ligarBlocosDeCodigo(bolha);
  ligarCitacoesInline(bolha, citacoes);
}

function ligarAcoes(el, msg, acoes) {
  el.querySelectorAll('.tmsg-acao').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const acao = btn.dataset.acao;
      if (acao === 'copiar') {
        navigator.clipboard && navigator.clipboard.writeText(msg.texto).catch(function () {});
        acoes.copiar(msg);
      } else if (acao === 'editar') {
        iniciarEdicao(el, msg, acoes);
      } else if (acao === 'regenerar') {
        acoes.regenerar(msg);
      } else if (acao === 'fixar') {
        const novo = !msg.fixada;
        btn.classList.toggle('on', novo);
        btn.setAttribute('aria-pressed', String(novo));
        acoes.fixar(msg, novo);
      } else if (acao === 'compartilhar') {
        acoes.compartilhar(msg);
      }
    });
  });
}

function iniciarEdicao(el, msg, acoes) {
  const bolha = el.querySelector('.tmsg-bubble');
  const original = bolha.innerHTML;
  bolha.innerHTML =
    '<textarea class="tmsg-editor" rows="3">' + msg.texto.replace(/</g, '&lt;') + '</textarea>' +
    '<div class="tmsg-editor-acoes">' +
      '<button type="button" class="btn btn-gho btn-sm" data-editor="cancelar">Cancelar</button>' +
      '<button type="button" class="btn btn-pri btn-sm" data-editor="salvar">Salvar e reenviar</button>' +
    '</div>';
  const area = bolha.querySelector('textarea');
  area.focus();
  area.setSelectionRange(area.value.length, area.value.length);

  bolha.querySelector('[data-editor="cancelar"]').addEventListener('click', function () {
    bolha.innerHTML = original;
  });
  bolha.querySelector('[data-editor="salvar"]').addEventListener('click', function () {
    const novoTexto = area.value.trim();
    if (!novoTexto) return;
    acoes.editarSalvar(msg, novoTexto);
  });
  area.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      bolha.querySelector('[data-editor="salvar"]').click();
    }
    if (e.key === 'Escape') { e.stopPropagation(); bolha.innerHTML = original; }
  });
}

function ligarQuiz(el, msg, acoes) {
  const grupo = el.querySelector('.tut-opts');
  if (!grupo) return;
  grupo.addEventListener('click', function (e) {
    const btn = e.target.closest('.tut-opt');
    if (!btn || grupo.classList.contains('respondido')) return;
    acoes.responderQuiz(msg, Number(btn.dataset.indice));
  });
}
