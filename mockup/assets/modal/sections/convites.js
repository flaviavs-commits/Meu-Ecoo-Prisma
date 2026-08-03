/* Secao "Convites" (workspace, so diretor): convidar gente nova e
   acompanhar quem ainda nao aceitou. */
import { avisar } from '../toast.js';
import { confirmar } from '../confirm.js';

let seq = 2;
const PENDENTES = [
  { id: 'c1', email: 'juliana.matos@horizonte.edu', papel: 'Professor', enviado: 'há 2 dias' },
  { id: 'c2', email: 'bruno.faria@horizonte.edu', papel: 'Coordenador', enviado: 'há 5 dias' },
];

function linha(c) {
  return (
    '<div class="rrow" data-id="' + c.id + '">' +
      '<span class="mic"><svg class="ic"><use href="#i-mail"/></svg></span>' +
      '<div class="tx"><b>' + c.email + '</b><span>' + c.papel + ' · convidado ' + c.enviado + '</span></div>' +
      '<div class="end">' +
        '<button type="button" class="pm-key-ico-btn" data-reenviar="' + c.id + '" aria-label="Reenviar convite"><svg class="ic"><use href="#i-refresh"/></svg></button>' +
        '<button type="button" class="btn btn-gho btn-sm" data-cancelar="' + c.id + '">Cancelar</button>' +
      '</div>' +
    '</div>'
  );
}

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Convites</h2>' +
      '<p>Convide novas pessoas para a instituição e acompanhe quem ainda não entrou.</p>' +
    '</div>' +
    '<div class="pm-grid-2" style="align-items:flex-end">' +
      '<div class="field" style="margin:0"><label>E-mail</label><input class="input" type="email" id="pm-conv-email" placeholder="nome@escola.edu"></div>' +
      '<div style="display:flex;gap:8px">' +
        '<div class="field" style="margin:0;flex:1"><label>Papel</label><select class="input" id="pm-conv-papel"><option>Professor</option><option>Coordenador</option><option>Diretor</option></select></div>' +
        '<button type="button" class="btn btn-pri" style="align-self:flex-end" data-acao="convidar"><span>Convidar</span></button>' +
      '</div>' +
    '</div>' +
    '<div id="pm-conv-banner"></div>' +
    '<div class="pm-sep"></div>' +
    '<h3 class="pm-subtitulo">Convites pendentes</h3>' +
    '<div id="pm-conv-lista">' + PENDENTES.map(linha).join('') + '</div>' +
    '<div class="pm-vazio" id="pm-conv-vazio" style="display:none">' +
      '<span class="pm-vazio-ic"><svg class="ic"><use href="#i-mail"/></svg></span>' +
      '<b>Nenhum convite pendente</b><span>Todo mundo que você convidou já entrou.</span>' +
    '</div>';

  const lista = container.querySelector('#pm-conv-lista');
  const vazio = container.querySelector('#pm-conv-vazio');

  function atualizarVazio() {
    const tem = lista.children.length > 0;
    lista.style.display = tem ? '' : 'none';
    vazio.style.display = tem ? 'none' : 'flex';
  }

  container.querySelector('[data-acao="convidar"]').addEventListener('click', function (e) {
    const email = container.querySelector('#pm-conv-email').value.trim();
    const papel = container.querySelector('#pm-conv-papel').value;
    const banner = container.querySelector('#pm-conv-banner');
    banner.innerHTML = '';
    if (!email || email.indexOf('@') === -1) {
      banner.innerHTML = '<div class="pm-banner pm-banner-erro"><svg class="ic"><use href="#i-alert"/></svg><span>Informe um e-mail válido.</span></div>';
      return;
    }
    window.PrismaCarregando(e.currentTarget, 'Enviando…', 800, function () {
      seq += 1;
      lista.insertAdjacentHTML('afterbegin', linha({ id: 'c' + seq, email: email, papel: papel, enviado: 'agora' }));
      ligarLinhas();
      container.querySelector('#pm-conv-email').value = '';
      atualizarVazio();
      banner.innerHTML = '<div class="pm-banner pm-banner-sucesso"><svg class="ic"><use href="#i-check"/></svg><span>Convite enviado para ' + email + '.</span></div>';
    });
  });

  function ligarLinhas() {
    lista.querySelectorAll('[data-reenviar]').forEach(function (btn) {
      if (btn.dataset.ligado) return;
      btn.dataset.ligado = '1';
      btn.addEventListener('click', function () { avisar('Convite reenviado', 'ok'); });
    });
    lista.querySelectorAll('[data-cancelar]').forEach(function (btn) {
      if (btn.dataset.ligado) return;
      btn.dataset.ligado = '1';
      btn.addEventListener('click', function () {
        const linhaEl = btn.closest('.rrow');
        const email = linhaEl.querySelector('b').textContent;
        confirmar({
          titulo: 'Cancelar convite?',
          descricao: email + ' não vai mais conseguir entrar com este convite.',
          rotuloConfirmar: 'Cancelar convite',
          perigo: true,
          aoConfirmar: function () { return new Promise(function (r) { setTimeout(r, 600); }); },
        }).then(function (ok) {
          if (!ok) return;
          linhaEl.remove();
          atualizarVazio();
          avisar('Convite cancelado', 'ok');
        });
      });
    });
  }
  ligarLinhas();
  atualizarVazio();
}
