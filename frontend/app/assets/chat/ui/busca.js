/* Busca dentro da conversa aberta: filtra as mensagens que contem o
   termo e deixa navegar entre elas (anterior/proximo), com contador.
   Opera no nivel de MENSAGEM (nao sublinha o trecho dentro da bolha)
   de proposito - mexer em texto ja renderizado como markdown arrisca
   quebrar tag pela metade; marcar a mensagem inteira e seguro e ainda
   assim resolve "achar onde eu falei sobre X". */
export function criarBuscaConversa(elFluxo, elBarra) {
  let ativa = false;
  let indiceAtual = 0;
  let alvos = [];

  elBarra.innerHTML =
    '<svg class="ic"><use href="#i-search"/></svg>' +
    '<input type="text" placeholder="Buscar nesta conversa…" aria-label="Buscar nesta conversa">' +
    '<span class="chat-busca-contagem"></span>' +
    '<button type="button" class="chat-busca-nav" data-dir="-1" aria-label="Anterior"><svg class="ic chat-chev-esq"><use href="#i-chev"/></svg></button>' +
    '<button type="button" class="chat-busca-nav" data-dir="1" aria-label="Próximo"><svg class="ic"><use href="#i-chev"/></svg></button>' +
    '<button type="button" class="chat-busca-fechar" aria-label="Fechar busca">✕</button>';

  const input = elBarra.querySelector('input');
  const contagem = elBarra.querySelector('.chat-busca-contagem');

  function limpar() {
    elFluxo.querySelectorAll('.chat-busca-oculta').forEach(function (el) { el.classList.remove('chat-busca-oculta'); });
    elFluxo.querySelectorAll('.chat-busca-alvo').forEach(function (el) { el.classList.remove('chat-busca-alvo'); });
  }

  function aplicar() {
    const q = input.value.trim().toLowerCase();
    limpar();
    const todas = Array.prototype.slice.call(elFluxo.querySelectorAll('.tmsg'));
    if (!q) { alvos = []; contagem.textContent = ''; return; }

    alvos = todas.filter(function (el) { return el.textContent.toLowerCase().includes(q); });
    todas.forEach(function (el) { if (alvos.indexOf(el) === -1) el.classList.add('chat-busca-oculta'); });
    indiceAtual = 0;
    pintarAlvo();
  }

  function pintarAlvo() {
    elFluxo.querySelectorAll('.chat-busca-alvo').forEach(function (el) { el.classList.remove('chat-busca-alvo'); });
    if (!alvos.length) { contagem.textContent = '0/0'; return; }
    const alvo = alvos[indiceAtual];
    alvo.classList.add('chat-busca-alvo');
    alvo.scrollIntoView({ behavior: 'smooth', block: 'center' });
    contagem.textContent = (indiceAtual + 1) + '/' + alvos.length;
  }

  function navegar(dir) {
    if (!alvos.length) return;
    indiceAtual = (indiceAtual + dir + alvos.length) % alvos.length;
    pintarAlvo();
  }

  input.addEventListener('input', aplicar);
  elBarra.querySelectorAll('.chat-busca-nav').forEach(function (b) {
    b.addEventListener('click', function () { navegar(Number(b.dataset.dir)); });
  });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); navegar(e.shiftKey ? -1 : 1); }
    if (e.key === 'Escape') { e.preventDefault(); fechar(); }
  });
  elBarra.querySelector('.chat-busca-fechar').addEventListener('click', fechar);

  function abrir() {
    ativa = true;
    elBarra.hidden = false;
    input.value = '';
    input.focus();
    limpar();
    contagem.textContent = '';
  }
  function fechar() {
    ativa = false;
    elBarra.hidden = true;
    limpar();
  }

  return {
    abrir: abrir,
    fechar: fechar,
    alternar: function () { if (ativa) fechar(); else abrir(); },
    estaAtiva: function () { return ativa; },
  };
}
