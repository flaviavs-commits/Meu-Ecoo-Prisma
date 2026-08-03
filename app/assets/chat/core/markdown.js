/* Conversor markdown -> HTML, escrito a mao (sem dependencia externa -
   o mockup nao tem bundler para empacotar uma lib de terceiro, so
   vendorizar um arquivo, e o subconjunto que o tutor realmente usa
   e pequeno). Cobre: titulos, negrito/italico, codigo inline e em
   bloco, links, listas (com/sem numero), citacao em bloco, tabela,
   regua horizontal e paragrafos. Sempre escapa HTML antes de aplicar
   qualquer regra - texto de entrada nunca vira marcacao por acidente. */
import { destacar } from './destaque.js';

function escaparHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** Regras inline, aplicadas na ordem (codigo primeiro, para o resto nao processar o que ja virou <code>). */
function inline(texto, citacoes) {
  let t = escaparHtml(texto);

  // Codigo inline: `x`
  t = t.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Negrito: **x** ou __x__
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/__([^_]+)__/g, '<strong>$1</strong>');

  // Italico: *x* ou _x_ (depois do negrito, para **x** nao virar italico duas vezes)
  t = t.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  t = t.replace(/_([^_]+)_/g, '<em>$1</em>');

  // Link: [texto](url) - so http(s) e ancora, nunca javascript:
  t = t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|#[^\s)]*)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

  // Citacao [n], so quando a mensagem tem citacoes com esse numero.
  if (citacoes && citacoes.length) {
    t = t.replace(/\[(\d+)\]/g, function (m, n) {
      const existe = citacoes.some(function (c) { return String(c.numero) === n; });
      return existe ? '<sup class="chat-cita" data-cita="' + n + '" tabindex="0" role="button">' + n + '</sup>' : m;
    });
  }

  return t;
}

function renderizarTabela(linhas) {
  const cabecalho = linhas[0].split('|').map(function (c) { return c.trim(); }).filter(Boolean);
  const corpo = linhas.slice(2).map(function (l) {
    return l.split('|').map(function (c) { return c.trim(); }).filter(Boolean);
  });
  let html = '<div class="chat-tabela-wrap"><table><thead><tr>';
  cabecalho.forEach(function (c) { html += '<th>' + inline(c) + '</th>'; });
  html += '</tr></thead><tbody>';
  corpo.forEach(function (linha) {
    html += '<tr>' + linha.map(function (c) { return '<td>' + inline(c) + '</td>'; }).join('') + '</tr>';
  });
  html += '</tbody></table></div>';
  return html;
}

/**
 * @param {string} origem
 * @param {{citacoes?: Array<{numero:number}>}} opcoes
 */
export function renderizarMarkdown(origem, opcoes) {
  const citacoes = (opcoes && opcoes.citacoes) || null;
  const linhas = origem.replace(/\r\n/g, '\n').split('\n');
  const blocos = [];
  let i = 0;

  while (i < linhas.length) {
    const linha = linhas[i];

    if (linha.trim() === '') { i++; continue; }

    // Bloco de codigo cercado ```lang
    const fence = linha.match(/^```(\w*)\s*$/);
    if (fence) {
      const idioma = fence[1] || 'text';
      const codigo = [];
      i++;
      while (i < linhas.length && !/^```\s*$/.test(linhas[i])) { codigo.push(linhas[i]); i++; }
      i++; // pula a cerca de fechamento
      blocos.push(renderizarBlocoCodigo(idioma, codigo.join('\n')));
      continue;
    }

    // Titulo
    const titulo = linha.match(/^(#{1,4})\s+(.*)$/);
    if (titulo) {
      const nivel = titulo[1].length + 2; // h3..h6 - h1/h2 sao da pagina, nao de mensagem de chat
      blocos.push('<h' + nivel + '>' + inline(titulo[2], citacoes) + '</h' + nivel + '>');
      i++; continue;
    }

    // Regua horizontal
    if (/^(-{3,}|\*{3,})\s*$/.test(linha)) { blocos.push('<hr>'); i++; continue; }

    // Tabela: linha com | seguida de linha separadora ---|---
    if (linha.includes('|') && linhas[i + 1] && /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$/.test(linhas[i + 1])) {
      const tabela = [linha, linhas[i + 1]];
      i += 2;
      while (i < linhas.length && linhas[i].includes('|')) { tabela.push(linhas[i]); i++; }
      blocos.push(renderizarTabela(tabela));
      continue;
    }

    // Citacao em bloco
    if (/^>\s?/.test(linha)) {
      const cit = [];
      while (i < linhas.length && /^>\s?/.test(linhas[i])) { cit.push(linhas[i].replace(/^>\s?/, '')); i++; }
      blocos.push('<blockquote>' + inline(cit.join(' '), citacoes) + '</blockquote>');
      continue;
    }

    // Lista (com ou sem numero) - mistura de - / * / 1. no mesmo bloco
    if (/^\s*([-*]|\d+\.)\s+/.test(linha)) {
      const ordenada = /^\s*\d+\.\s+/.test(linha);
      const itens = [];
      while (i < linhas.length && /^\s*([-*]|\d+\.)\s+/.test(linhas[i])) {
        itens.push(linhas[i].replace(/^\s*([-*]|\d+\.)\s+/, ''));
        i++;
      }
      const tag = ordenada ? 'ol' : 'ul';
      blocos.push('<' + tag + '>' + itens.map(function (it) { return '<li>' + inline(it, citacoes) + '</li>'; }).join('') + '</' + tag + '>');
      continue;
    }

    // Paragrafo: junta linhas seguidas ate uma linha em branco
    const par = [linha];
    i++;
    while (i < linhas.length && linhas[i].trim() !== '' && !/^```|^#{1,4}\s|^>|^\s*([-*]|\d+\.)\s|^(-{3,}|\*{3,})\s*$/.test(linhas[i])) {
      par.push(linhas[i]); i++;
    }
    blocos.push('<p>' + inline(par.join(' '), citacoes) + '</p>');
  }

  return blocos.join('\n');
}

function renderizarBlocoCodigo(idioma, codigo) {
  const html = destacar(codigo, idioma);
  const nLinhas = codigo.split('\n').length;
  return (
    '<pre class="chat-code" data-lang="' + escaparHtml(idioma) + '" data-linhas="' + nLinhas + '">' +
    '<code>' + html + '</code></pre>'
  );
}
