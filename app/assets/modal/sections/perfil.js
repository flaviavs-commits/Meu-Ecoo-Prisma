/* Secao "Perfil" do modal de Configuracoes: avatar, dados pessoais
   editaveis e um resumo em numeros - equivalente direto do antigo
   `#modal-conta`, agora vivendo dentro da casca compartilhada. */
import { avisar } from '../toast.js';

export function montar(container, ctx) {
  const p = ctx.perfil;
  const stats = (p.stats || []).map(function (s) {
    return '<div><b>' + s.valor + '</b><span>' + s.rotulo + '</span></div>';
  }).join('');

  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Pessoal</p>' +
      '<h2>Perfil</h2>' +
      '<p>Como seu nome e contato aparecem para o resto da instituição.</p>' +
    '</div>' +
    '<div class="pm-perfil-card">' +
      '<span class="pm-settings-av pm-perfil-av" style="' + (p.cor ? 'background:' + p.cor : '') + '">' + (p.iniciais || '') + '</span>' +
      '<div class="pm-perfil-quem"><b>' + p.nome + '</b><span>' + p.cargo + '</span></div>' +
      '<button type="button" class="btn btn-gho btn-sm" data-acao="foto">Alterar foto</button>' +
    '</div>' +
    '<div class="pm-perfil-stats">' + stats + '</div>' +
    '<div class="pm-sep"></div>' +
    '<div class="pm-grid-2">' +
      '<div class="field" style="margin:0"><label>Nome completo</label><input class="input" id="pm-pf-nome" value="' + (p.nome || '') + '"></div>' +
      '<div class="field" style="margin:0"><label>E-mail</label><input class="input" type="email" id="pm-pf-email" value="' + (p.email || '') + '"></div>' +
      '<div class="field" style="margin:0"><label>' + (p.tipo === 'diretor' ? 'Cargo' : 'Telefone') + '</label><input class="input" id="pm-pf-extra" value="' + (p.tipo === 'diretor' ? (p.cargoCompleto || p.cargo) : (p.telefone || '')) + '"></div>' +
      '<div class="field" style="margin:0"><label>Telefone</label><input class="input" id="pm-pf-tel2" value="' + (p.telefone || '') + '" ' + (p.tipo === 'diretor' ? '' : 'style="display:none"') + '></div>' +
    '</div>' +
    '<div class="pm-acoes-dir"><button type="button" class="btn btn-pri" data-acao="salvar">Salvar alterações</button></div>' +
    '<div id="pm-pf-banner"></div>';

  if (p.tipo !== 'diretor') {
    container.querySelector('#pm-pf-tel2').closest('.field').remove();
  }

  container.querySelector('[data-acao="foto"]').addEventListener('click', function () {
    avisar('Envio de foto ainda não está disponível nesta demonstração.', 'aviso');
  });

  container.querySelector('[data-acao="salvar"]').addEventListener('click', function (e) {
    const btn = e.currentTarget;
    if (typeof window.PrismaCarregando === 'function') {
      window.PrismaCarregando(btn, 'Salvando…', 850, function () { avisar('Alterações salvas', 'ok'); });
    } else {
      avisar('Alterações salvas', 'ok');
    }
  });
}
