/* Catalogo de secoes do modal de Configuracoes: quem existe, em que
   grupo, com que icone, e para quais perfis. `settings.js` so consome
   esta lista - novas secoes entram aqui, nao espalhadas pelo resto do
   sistema. */
import * as perfil from './sections/perfil.js';
import * as notificacoes from './sections/notificacoes.js';
import * as preferencias from './sections/preferencias.js';
import * as seguranca from './sections/seguranca.js';
import * as ajuda from './sections/ajuda.js';
import * as feedback from './sections/feedback.js';
import * as plano from './sections/plano.js';
import * as billing from './sections/billing.js';
import * as apikeys from './sections/apikeys.js';
import * as equipe from './sections/equipe.js';
import * as permissoes from './sections/permissoes.js';
import * as convites from './sections/convites.js';
import * as workspace from './sections/workspace.js';
import * as historico from './sections/historico.js';
import * as logs from './sections/logs.js';

export const GRUPOS = [
  { id: 'pessoal', rotulo: 'Pessoal' },
  { id: 'workspace', rotulo: 'Espaço de trabalho' },
];

const TODAS = [
  { id: 'perfil', grupo: 'pessoal', rotulo: 'Perfil', icone: 'i-user', montar: perfil.montar },
  { id: 'notificacoes', grupo: 'pessoal', rotulo: 'Notificações', icone: 'i-bell', montar: notificacoes.montar },
  { id: 'preferencias', grupo: 'pessoal', rotulo: 'Preferências', icone: 'i-cog', montar: preferencias.montar },
  { id: 'seguranca', grupo: 'pessoal', rotulo: 'Segurança', icone: 'i-shield', montar: seguranca.montar },
  { id: 'ajuda', grupo: 'pessoal', rotulo: 'Ajuda', icone: 'i-help', montar: ajuda.montar },
  { id: 'feedback', grupo: 'pessoal', rotulo: 'Feedback', icone: 'i-message', montar: feedback.montar },

  { id: 'plano', grupo: 'workspace', rotulo: 'Plano e assinatura', icone: 'i-coin', somentePerfis: ['diretor'], montar: plano.montar },
  { id: 'billing', grupo: 'workspace', rotulo: 'Faturamento', icone: 'i-wallet', somentePerfis: ['diretor'], montar: billing.montar },
  { id: 'apikeys', grupo: 'workspace', rotulo: 'Chaves de API', icone: 'i-key', somentePerfis: ['diretor'], montar: apikeys.montar },
  { id: 'equipe', grupo: 'workspace', rotulo: 'Equipe', icone: 'i-users', somentePerfis: ['diretor'], montar: equipe.montar },
  { id: 'permissoes', grupo: 'workspace', rotulo: 'Permissões', icone: 'i-lock', somentePerfis: ['diretor'], montar: permissoes.montar },
  { id: 'convites', grupo: 'workspace', rotulo: 'Convites', icone: 'i-plus', somentePerfis: ['diretor'], montar: convites.montar },
  { id: 'workspace', grupo: 'workspace', rotulo: 'Instituição', icone: 'i-briefcase', somentePerfis: ['diretor'], montar: workspace.montar },
  { id: 'historico', grupo: 'workspace', rotulo: 'Histórico', icone: 'i-clock', somentePerfis: ['diretor'], montar: historico.montar },
  { id: 'logs', grupo: 'workspace', rotulo: 'Logs', icone: 'i-doc', somentePerfis: ['diretor'], montar: logs.montar },
];

export function secoesParaPerfil(tipoPerfil) {
  return TODAS.filter(function (s) {
    return !s.somentePerfis || s.somentePerfis.indexOf(tipoPerfil) !== -1;
  });
}
