/* Realce de sintaxe leve, por expressao regular - nao e um parser real
   de cada linguagem (isso pediria uma gramatica por idioma, fora de
   escopo para um mockup sem build step), e sim reconhecimento visual
   suficiente para comentario/string/numero/palavra-chave ficarem
   diferenciados, como qualquer editor faria numa previa. `diff` foge
   da regra: e realce por LINHA (+ / -), nao por token. */

function escaparHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const PALAVRAS = {
  js: 'const let var function return if else for while class extends new this import export default from async await try catch finally throw typeof instanceof in of switch case break continue null undefined true false static get set super yield void delete',
  ts: 'const let var function return if else for while class extends implements interface type enum public private protected readonly new this import export default from async await try catch finally throw typeof instanceof in of switch case break continue null undefined true false static get set super yield void delete as',
  python: 'def return if elif else for while class import from as try except finally raise with lambda yield pass break continue in is not and or None True False self global nonlocal async await',
  json: 'true false null',
  bash: 'if then else fi for while do done case esac function return export local echo cd',
};
PALAVRAS.jsx = PALAVRAS.js;
PALAVRAS.tsx = PALAVRAS.ts;
PALAVRAS.py = PALAVRAS.python;
PALAVRAS.sh = PALAVRAS.bash;
PALAVRAS.shell = PALAVRAS.bash;

/** Linguagens "C-like": comentario //, string com aspas, numero, palavra-chave. */
function destacarGenerico(codigo, idioma) {
  const chavesLista = PALAVRAS[idioma];
  if (!chavesLista) return escaparHtml(codigo);
  const chaves = new Set(chavesLista.split(' '));
  const comentarioLinha = idioma === 'python' || idioma === 'bash' ? '#' : '//';

  // Um passe so, alternando os padroes por prioridade - comentario e
  // string "vencem" para o resto do trecho nao ser tokenizado por dentro.
  const padrao = new RegExp(
    '(' + comentarioLinha + '[^\\n]*)' +           // 1: comentario
    '|("(?:[^"\\\\]|\\\\.)*"|\'(?:[^\'\\\\]|\\\\.)*\')' + // 2: string
    '|(\\b\\d+(?:\\.\\d+)?\\b)' +                    // 3: numero
    '|(\\b[a-zA-Z_]\\w*\\b)',                          // 4: identificador (filtrado por `chaves` depois)
    'g',
  );

  let saida = '';
  let ultimo = 0;
  let m;
  while ((m = padrao.exec(codigo))) {
    saida += escaparHtml(codigo.slice(ultimo, m.index));
    if (m[1]) saida += '<span class="tok-com">' + escaparHtml(m[1]) + '</span>';
    else if (m[2]) saida += '<span class="tok-str">' + escaparHtml(m[2]) + '</span>';
    else if (m[3]) saida += '<span class="tok-num">' + escaparHtml(m[3]) + '</span>';
    else if (m[4]) saida += chaves.has(m[4]) ? '<span class="tok-kw">' + m[4] + '</span>' : m[4];
    ultimo = padrao.lastIndex;
  }
  saida += escaparHtml(codigo.slice(ultimo));
  return saida;
}

/** HTML: nome de tag e atributo recebem cor, o resto fica neutro. */
function destacarHtml(codigo) {
  return escaparHtml(codigo).replace(
    /(&lt;\/?)([a-zA-Z][\w-]*)((?:\s+[\w-]+(?:=(?:"[^"]*"|'[^']*'))?)*)(\s*\/?&gt;)/g,
    function (_m, abre, tag, atrs, fecha) {
      const atrsRealcados = atrs.replace(/([\w-]+)(=)("[^"]*"|'[^']*')/g, '<span class="tok-attr">$1</span>$2<span class="tok-str">$3</span>');
      return abre + '<span class="tok-kw">' + tag + '</span>' + atrsRealcados + fecha;
    },
  );
}

/** CSS: seletor antes de `{`, propriedade antes de `:`, valor depois. */
function destacarCss(codigo) {
  return escaparHtml(codigo)
    .replace(/([.#]?[\w-]+)(\s*\{)/g, '<span class="tok-kw">$1</span>$2')
    .replace(/([\w-]+)(\s*:)(\s*[^;]+;?)/g, '<span class="tok-attr">$1</span>$2<span class="tok-str">$3</span>');
}

/** Diff: realce por linha, nao por token - `+` adiciona, `-` remove, resto e contexto. */
function destacarDiff(codigo) {
  return codigo.split('\n').map(function (linha) {
    if (linha.startsWith('+')) return '<span class="chat-diff-add">' + escaparHtml(linha) + '</span>';
    if (linha.startsWith('-')) return '<span class="chat-diff-del">' + escaparHtml(linha) + '</span>';
    return '<span class="chat-diff-ctx">' + escaparHtml(linha) + '</span>';
  }).join('\n');
}

export function destacar(codigo, idioma) {
  const lang = (idioma || 'text').toLowerCase();
  if (lang === 'diff' || lang === 'patch') return destacarDiff(codigo);
  if (lang === 'html' || lang === 'xml' || lang === 'svg') return destacarHtml(codigo);
  if (lang === 'css') return destacarCss(codigo);
  if (PALAVRAS[lang]) return destacarGenerico(codigo, lang);
  return escaparHtml(codigo);
}
