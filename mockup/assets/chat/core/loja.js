/* Loja central do chat: unica fonte de verdade para conversas, pastas
   e qual conversa esta ativa. Persiste no localStorage a cada mutacao
   e notifica assinantes (padrao pub-sub simples) - a UI nunca guarda
   copia propria do estado, so re-renderiza quando a loja avisa. */
import { carregar, salvar } from './armazenamento.js';
import { criarConversa, criarMensagem, criarPasta } from './modelo.js';
import { conversasSemente } from './semente.js';

let estado = carregar() || {
  conversas: conversasSemente(),
  pastas: [],
  conversaAtivaId: null,
};
if (!estado.conversaAtivaId && estado.conversas.length) {
  estado.conversaAtivaId = estado.conversas[0].id;
}

const ouvintes = new Set();
function notificar() {
  salvar(estado);
  ouvintes.forEach(function (fn) { fn(estado); });
}

/** @param {(estado: object) => void} fn @returns {() => void} cancelar a assinatura */
export function assinar(fn) {
  ouvintes.add(fn);
  fn(estado);
  return function () { ouvintes.delete(fn); };
}

export function obterEstado() { return estado; }
export function obterConversa(id) { return estado.conversas.find(function (c) { return c.id === id; }); }
export function conversaAtiva() { return obterConversa(estado.conversaAtivaId); }

export function ativarConversa(id) {
  if (!obterConversa(id)) return;
  estado.conversaAtivaId = id;
  notificar();
}

export function novaConversa(materiaId, titulo) {
  const c = criarConversa({ materiaId: materiaId, titulo: titulo || 'Nova conversa' });
  estado.conversas.unshift(c);
  estado.conversaAtivaId = c.id;
  notificar();
  return c;
}

export function excluirConversa(id) {
  estado.conversas = estado.conversas.filter(function (c) { return c.id !== id; });
  if (estado.conversaAtivaId === id) {
    estado.conversaAtivaId = estado.conversas.length ? estado.conversas[0].id : null;
  }
  notificar();
}

export function renomearConversa(id, titulo) {
  const c = obterConversa(id);
  if (!c || !titulo.trim()) return;
  c.titulo = titulo.trim();
  c.atualizadaEm = Date.now();
  notificar();
}

export function favoritarConversa(id, favorita) {
  const c = obterConversa(id);
  if (!c) return;
  c.favorita = favorita;
  notificar();
}

export function moverParaPasta(idConversa, idPasta) {
  const c = obterConversa(idConversa);
  if (!c) return;
  c.pastaId = idPasta;
  notificar();
}

export function alternarTag(idConversa, tag) {
  const c = obterConversa(idConversa);
  if (!c) return;
  const i = c.tags.indexOf(tag);
  if (i === -1) c.tags.push(tag); else c.tags.splice(i, 1);
  notificar();
}

export function criarPastaNaLoja(nome) {
  if (!nome.trim()) return null;
  const p = criarPasta(nome.trim());
  estado.pastas.push(p);
  notificar();
  return p;
}

export function renomearPasta(id, nome) {
  const p = estado.pastas.find(function (x) { return x.id === id; });
  if (!p || !nome.trim()) return;
  p.nome = nome.trim();
  notificar();
}

export function excluirPasta(id) {
  estado.pastas = estado.pastas.filter(function (p) { return p.id !== id; });
  estado.conversas.forEach(function (c) { if (c.pastaId === id) c.pastaId = null; });
  notificar();
}

/** Acrescenta uma mensagem pronta (sem streaming) e retorna ela. */
export function adicionarMensagem(idConversa, dadosMensagem) {
  const c = obterConversa(idConversa);
  if (!c) return null;
  const msg = criarMensagem(dadosMensagem);
  c.mensagens.push(msg);
  c.atualizadaEm = Date.now();
  notificar();
  return msg;
}

/** Atualiza campos de uma mensagem existente (usado pelo streaming a cada chunk). */
export function atualizarMensagem(idConversa, idMensagem, patch) {
  const c = obterConversa(idConversa);
  if (!c) return;
  const m = c.mensagens.find(function (x) { return x.id === idMensagem; });
  if (!m) return;
  Object.assign(m, patch);
  notificar();
}

export function fixarMensagem(idConversa, idMensagem, fixada) {
  const c = obterConversa(idConversa);
  if (!c) return;
  const m = c.mensagens.find(function (x) { return x.id === idMensagem; });
  if (!m) return;
  m.fixada = fixada;
  notificar();
}

/** Remove esta mensagem e tudo que veio depois - base de "editar" e "regenerar". */
export function truncarApartirDe(idConversa, idMensagem) {
  const c = obterConversa(idConversa);
  if (!c) return;
  const i = c.mensagens.findIndex(function (x) { return x.id === idMensagem; });
  if (i === -1) return;
  c.mensagens = c.mensagens.slice(0, i);
  notificar();
}

/** Remove so as mensagens DEPOIS desta (mantem a propria) - base de "regenerar". */
export function truncarDepoisDe(idConversa, idMensagem) {
  const c = obterConversa(idConversa);
  if (!c) return;
  const i = c.mensagens.findIndex(function (x) { return x.id === idMensagem; });
  if (i === -1) return;
  c.mensagens = c.mensagens.slice(0, i + 1);
  notificar();
}

export function todasAsConversas() { return estado.conversas; }
export function todasAsPastas() { return estado.pastas; }
