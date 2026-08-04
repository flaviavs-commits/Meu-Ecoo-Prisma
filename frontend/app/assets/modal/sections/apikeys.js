/* Secao "Chaves de API" (workspace, so diretor). O momento que mais
   importa aqui e a criacao: a chave completa so aparece uma vez, igual
   Stripe/OpenAI - depois disso so o valor mascarado fica visivel. */
import { avisar } from '../toast.js';
import { confirmar } from '../confirm.js';

let seq = 3;
const CHAVES = [
  { id: 'k1', nome: 'Integração — boletim PDF', mascara: 'prsm_live_••••••••••••7f2a', criada: '12/06/2026', uso: 'há 3 dias' },
  { id: 'k2', nome: 'Backup noturno', mascara: 'prsm_live_••••••••••••c910', criada: '02/03/2026', uso: 'há 1 dia' },
];

function linhaChave(k) {
  return (
    '<div class="rrow" data-id="' + k.id + '">' +
      '<span class="mic"><svg class="ic"><use href="#i-key"/></svg></span>' +
      '<div class="tx"><b>' + k.nome + '</b><span class="pm-key-valor" style="display:inline-block;margin-top:4px;padding:3px 8px">' + k.mascara + '</span><span style="display:block;margin-top:3px">criada em ' + k.criada + ' · usada ' + k.uso + '</span></div>' +
      '<div class="end"><button type="button" class="btn btn-gho btn-sm" data-revogar="' + k.id + '"><svg class="ic"><use href="#i-trash"/></svg><span>Revogar</span></button></div>' +
    '</div>'
  );
}

export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Chaves de API</h2>' +
      '<p>Usadas por integrações externas para falar com o Prisma em nome da instituição.</p>' +
    '</div>' +
    '<div id="pm-keys-revelada"></div>' +
    '<div class="pm-acoes-dir" style="justify-content:flex-start;margin:0 0 6px">' +
      '<button type="button" class="btn btn-pri btn-sm" data-acao="gerar"><svg class="ic"><use href="#i-plus"/></svg><span>Gerar nova chave</span></button>' +
    '</div>' +
    '<div id="pm-keys-lista">' + CHAVES.map(linhaChave).join('') + '</div>';

  const lista = container.querySelector('#pm-keys-lista');
  const revelPanel = container.querySelector('#pm-keys-revelada');

  container.querySelector('[data-acao="gerar"]').addEventListener('click', function (e) {
    window.PrismaCarregando(e.currentTarget, 'Gerando…', 900, function () {
      seq += 1;
      const chaveCompleta = 'prsm_live_' + Math.random().toString(36).slice(2, 10) + Math.random().toString(36).slice(2, 10);
      const novo = { id: 'k' + seq, nome: 'Nova chave', mascara: 'prsm_live_••••••••••••' + chaveCompleta.slice(-4), criada: 'agora', uso: 'nunca' };
      CHAVES.unshift(novo);

      revelPanel.innerHTML =
        '<div class="pm-key-revelada">' +
          '<b>Copie agora — esta chave não será mostrada novamente</b>' +
          '<div class="pm-key-row">' +
            '<span class="pm-key-valor" id="pm-keys-valor-novo">' + chaveCompleta + '</span>' +
            '<button type="button" class="pm-key-ico-btn" data-copiar aria-label="Copiar chave"><svg class="ic"><use href="#i-copy"/></svg></button>' +
          '</div>' +
        '</div>';
      lista.insertAdjacentHTML('afterbegin', linhaChave(novo));
      ligarRevogar();

      revelPanel.querySelector('[data-copiar]').addEventListener('click', function (ev) {
        const btn = ev.currentTarget;
        if (navigator.clipboard) navigator.clipboard.writeText(chaveCompleta).catch(function () {});
        btn.classList.add('pm-copiado');
        btn.innerHTML = '<svg class="ic"><use href="#i-check"/></svg>';
        avisar('Chave copiada', 'ok');
      });
    });
  });

  function ligarRevogar() {
    lista.querySelectorAll('[data-revogar]').forEach(function (btn) {
      if (btn.dataset.ligado) return;
      btn.dataset.ligado = '1';
      btn.addEventListener('click', function () {
        const linha = btn.closest('.rrow');
        const nome = linha.querySelector('b').textContent;
        confirmar({
          titulo: 'Revogar "' + nome + '"?',
          descricao: 'Qualquer integração usando esta chave para de funcionar imediatamente.',
          rotuloConfirmar: 'Revogar chave',
          perigo: true,
          aoConfirmar: function () { return new Promise(function (r) { setTimeout(r, 700); }); },
        }).then(function (ok) {
          if (!ok) return;
          const pai = linha.parentNode;
          const proximo = linha.nextSibling;
          linha.remove();
          if (window.PrismaToastUndo) window.PrismaToastUndo('Chave revogada', function () { pai.insertBefore(linha, proximo); });
          avisar('Chave revogada', 'ok');
        });
      });
    });
  }
  ligarRevogar();
}
