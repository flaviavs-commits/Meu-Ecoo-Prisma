/* Secao "Segurança": trocar senha, sessões ativas, dispositivos
   conectados e a zona de perigo (excluir conta). Cada lista tem sua
   propria confirmacao antes de remover algo - nada some com um clique
   so, o padrao do resto do produto para acoes que nao voltam atras. */
import { avisar } from '../toast.js';
import { confirmar } from '../confirm.js';

const SESSOES = [
  { id: 's1', dispositivo: 'Chrome · Windows', local: 'São Paulo, BR', quando: 'ativa agora', atual: true },
  { id: 's2', dispositivo: 'Safari · iPhone 14', local: 'São Paulo, BR', quando: 'há 2 horas', atual: false },
  { id: 's3', dispositivo: 'Chrome · Windows', local: 'Campinas, BR', quando: 'há 6 dias', atual: false },
];

const DISPOSITIVOS = [
  { id: 'd1', nome: 'Notebook pessoal', tipo: 'Windows 11 · Chrome', quando: 'usado agora' },
  { id: 'd2', nome: 'iPhone 14', tipo: 'iOS 18 · Safari', quando: 'usado há 2 horas' },
];

function iconeOlho(mostrando) {
  return '<svg class="ic"><use href="#' + (mostrando ? 'i-eye-off' : 'i-eye') + '"/></svg>';
}

function campoSenha(id, rotulo) {
  return (
    '<div class="field" style="margin:0">' +
      '<label>' + rotulo + '</label>' +
      '<div style="position:relative">' +
        '<input class="input" type="password" id="' + id + '" style="padding-right:38px" autocomplete="new-password">' +
        '<button type="button" class="pm-key-ico-btn" data-olho="' + id + '" style="position:absolute;right:4px;top:50%;transform:translateY(-50%);border:0;background:transparent" aria-label="Mostrar senha">' + iconeOlho(false) + '</button>' +
      '</div>' +
    '</div>'
  );
}

function linhaSessaoOuDispositivo(item, rotuloRemover) {
  return (
    '<div class="rrow" data-id="' + item.id + '">' +
      '<span class="mic"><svg class="ic"><use href="#i-monitor"/></svg></span>' +
      '<div class="tx"><b>' + (item.dispositivo || item.nome) + (item.atual ? ' <span class="pill p-ok" style="margin-left:6px">este dispositivo</span>' : '') + '</b>' +
      '<span>' + (item.local || item.tipo) + ' · ' + item.quando + '</span></div>' +
      (item.atual ? '' : '<div class="end"><button type="button" class="btn btn-gho btn-sm" data-remover="' + item.id + '">' + rotuloRemover + '</button></div>') +
    '</div>'
  );
}

export function montar(container, ctx) {
  const p = ctx.perfil;

  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Pessoal</p>' +
      '<h2>Segurança</h2>' +
      '<p>Senha, sessões ativas e dispositivos com acesso à sua conta.</p>' +
    '</div>' +

    '<h3 class="pm-subtitulo">Alterar senha</h3>' +
    '<div class="pm-grid-2">' +
      campoSenha('pm-sg-atual', 'Senha atual') +
      '<div></div>' +
      campoSenha('pm-sg-nova', 'Nova senha') +
      campoSenha('pm-sg-conf', 'Confirmar nova senha') +
    '</div>' +
    '<div class="pm-acoes-dir"><button type="button" class="btn btn-pri" data-acao="trocar-senha">Atualizar senha</button></div>' +
    '<div id="pm-sg-senha-banner"></div>' +

    '<div class="pm-sep"></div>' +
    '<h3 class="pm-subtitulo">Sessões ativas</h3>' +
    '<div id="pm-sg-sessoes">' + SESSOES.map(function (s) { return linhaSessaoOuDispositivo(s, 'Encerrar'); }).join('') + '</div>' +

    '<div class="pm-sep"></div>' +
    '<h3 class="pm-subtitulo">Dispositivos conectados</h3>' +
    '<div id="pm-sg-dispositivos">' + DISPOSITIVOS.map(function (d) { return linhaSessaoOuDispositivo(d, 'Remover'); }).join('') + '</div>' +

    '<div class="pm-sep"></div>' +
    '<h3 class="pm-subtitulo pm-subtitulo-perigo">Zona de perigo</h3>' +
    '<div class="pm-perigo">' +
      '<div class="pm-perigo-linha">' +
        '<div><b>Excluir conta</b><span>Remove seu acesso e seus dados pessoais permanentemente.</span></div>' +
        '<button type="button" class="btn btn-danger btn-sm" data-acao="excluir-conta"><svg class="ic"><use href="#i-trash"/></svg><span>Excluir</span></button>' +
      '</div>' +
    '</div>';

  container.querySelectorAll('[data-olho]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const input = container.querySelector('#' + btn.dataset.olho);
      const mostrando = input.type === 'text';
      input.type = mostrando ? 'password' : 'text';
      btn.innerHTML = iconeOlho(!mostrando);
      btn.setAttribute('aria-label', mostrando ? 'Mostrar senha' : 'Ocultar senha');
    });
  });

  container.querySelector('[data-acao="trocar-senha"]').addEventListener('click', function (e) {
    const nova = container.querySelector('#pm-sg-nova').value;
    const conf = container.querySelector('#pm-sg-conf').value;
    const banner = container.querySelector('#pm-sg-senha-banner');
    banner.innerHTML = '';
    if (!nova || nova !== conf) {
      banner.innerHTML = '<div class="pm-banner pm-banner-erro"><svg class="ic"><use href="#i-alert"/></svg><span>As senhas não coincidem.</span></div>';
      return;
    }
    const btn = e.currentTarget;
    window.PrismaCarregando(btn, 'Atualizando…', 900, function () {
      banner.innerHTML = '<div class="pm-banner pm-banner-sucesso"><svg class="ic"><use href="#i-check"/></svg><span>Senha atualizada.</span></div>';
      ['pm-sg-atual', 'pm-sg-nova', 'pm-sg-conf'].forEach(function (id) { container.querySelector('#' + id).value = ''; });
    });
  });

  container.querySelector('#pm-sg-sessoes').addEventListener('click', function (e) {
    const btn = e.target.closest('[data-remover]');
    if (!btn) return;
    const linha = btn.closest('.rrow');
    confirmar({
      titulo: 'Encerrar esta sessão?',
      descricao: 'O dispositivo vai precisar entrar novamente para acessar a conta.',
      rotuloConfirmar: 'Encerrar sessão',
      perigo: true,
      aoConfirmar: function () { return new Promise(function (r) { setTimeout(r, 700); }); },
    }).then(function (ok) {
      if (!ok) return;
      linha.remove();
      avisar('Sessão encerrada', 'ok');
    });
  });

  container.querySelector('#pm-sg-dispositivos').addEventListener('click', function (e) {
    const btn = e.target.closest('[data-remover]');
    if (!btn) return;
    const linha = btn.closest('.rrow');
    confirmar({
      titulo: 'Remover este dispositivo?',
      descricao: 'Ele deixará de ter acesso à sua conta imediatamente.',
      rotuloConfirmar: 'Remover',
      perigo: true,
      aoConfirmar: function () { return new Promise(function (r) { setTimeout(r, 700); }); },
    }).then(function (ok) {
      if (!ok) return;
      linha.remove();
      avisar('Dispositivo removido', 'ok');
    });
  });

  container.querySelector('[data-acao="excluir-conta"]').addEventListener('click', function () {
    confirmar({
      titulo: 'Excluir sua conta?',
      descricao: 'Essa ação é permanente. Todo o seu histórico, materiais salvos e progresso serão perdidos' + (p.tipo === 'diretor' ? ', incluindo o acesso administrativo à instituição.' : '.'),
      rotuloConfirmar: 'Excluir minha conta',
      perigo: true,
      textoParaDigitar: 'EXCLUIR',
      aoConfirmar: function () { return new Promise(function (r) { setTimeout(r, 1100); }); },
    }).then(function (ok) {
      if (ok) avisar('Conta marcada para exclusão. Você será desconectado.', 'ok');
    });
  });
}
