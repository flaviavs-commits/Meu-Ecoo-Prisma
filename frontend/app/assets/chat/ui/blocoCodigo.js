/* Envolve todo `<pre class="chat-code">` (ja com o realce aplicado por
   `core/destaque.js`) numa moldura premium: rotulo da linguagem,
   contagem de linhas e botao de copiar. Roda depois do markdown
   injetar o HTML - nao faz parte do parser, so decora o resultado. */
export function ligarBlocosDeCodigo(container) {
  container.querySelectorAll('pre.chat-code').forEach(function (pre) {
    if (pre.dataset.montado) return;
    pre.dataset.montado = '1';

    const idioma = pre.dataset.lang || 'text';
    const nLinhas = pre.dataset.linhas || '1';
    const ehDiff = idioma === 'diff' || idioma === 'patch';

    const cabecalho = document.createElement('div');
    cabecalho.className = 'chat-code-head';
    cabecalho.innerHTML =
      '<span class="chat-code-lang">' + (ehDiff ? 'diff' : idioma) + '</span>' +
      '<span class="chat-code-linhas">' + nLinhas + ' linha' + (nLinhas === '1' ? '' : 's') + '</span>' +
      '<button type="button" class="chat-code-copiar" aria-label="Copiar código">' +
        '<svg class="ic"><use href="#i-copy"/></svg><span>Copiar</span>' +
      '</button>';

    const wrap = document.createElement('div');
    wrap.className = 'chat-code-wrap' + (ehDiff ? ' chat-code-diff' : '');
    pre.replaceWith(wrap);
    wrap.appendChild(cabecalho);
    wrap.appendChild(pre);

    cabecalho.querySelector('.chat-code-copiar').addEventListener('click', function (e) {
      const btn = e.currentTarget;
      const codigo = pre.querySelector('code').textContent;
      if (navigator.clipboard) navigator.clipboard.writeText(codigo).catch(function () {});
      const original = btn.innerHTML;
      btn.classList.add('copiado');
      btn.innerHTML = '<svg class="ic"><use href="#i-check"/></svg><span>Copiado</span>';
      setTimeout(function () { btn.classList.remove('copiado'); btn.innerHTML = original; }, 1600);
    });
  });
}
