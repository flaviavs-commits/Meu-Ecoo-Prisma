/* Composer do tutor: textarea que cresce sozinha, anexos pendentes
   (com preview), arrastar-e-soltar na area toda do chat, acoes
   rapidas, e o botao que vira "Parar" enquanto o tutor esta
   respondendo. So sabe de UI - quem decide o que fazer com o texto
   enviado e quem instancia isto (`ctx.aoEnviar`). */
const ACOES_RAPIDAS = [
  { rotulo: 'Só explicar', icone: 'i-doc', texto: 'Só explica de novo, sem pergunta.' },
  { rotulo: 'Dar uma dica', icone: 'i-spark', texto: 'Me dá uma dica, sem entregar a resposta.' },
  { rotulo: '3 parecidas', icone: 'i-cards', texto: 'Separa 3 questões parecidas com essa.' },
];

function iconeEnviar() {
  return '<svg><use href="#i-send"/></svg>';
}
function iconeParar() {
  return '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';
}

/**
 * @param {HTMLElement} container
 * @param {{aoEnviar:(texto:string, anexos:Array)=>void, aoParar:()=>void, estaRespondendo:()=>boolean}} ctx
 * @returns {{focar:()=>void, anexarArquivos:(FileList)=>void}}
 */
export function criarComposer(container, ctx) {
  let anexosPendentes = [];

  container.innerHTML =
    '<div class="tut-flow">' +
      '<div class="chat-anexos-pendentes" hidden></div>' +
      '<div class="tut-quick">' +
        ACOES_RAPIDAS.map(function (a) {
          return '<button type="button" data-rapida="' + a.texto.replace(/"/g, '&quot;') + '"><svg class="ic"><use href="#' + a.icone + '"/></svg><span>' + a.rotulo + '</span></button>';
        }).join('') +
      '</div>' +
      '<div class="tut-input">' +
        '<textarea rows="1" placeholder="Responder ao tutor…" aria-label="Resposta"></textarea>' +
        '<button type="button" class="chat-anexar" aria-label="Anexar arquivo"><svg class="ic"><use href="#i-doc"/></svg></button>' +
        '<button type="button" class="tut-send" aria-label="Enviar"></button>' +
        '<input type="file" multiple hidden class="chat-input-arquivo">' +
      '</div>' +
    '</div>';

  const area = container.querySelector('textarea');
  const btnEnviar = container.querySelector('.tut-send');
  const btnAnexar = container.querySelector('.chat-anexar');
  const inputArquivo = container.querySelector('.chat-input-arquivo');
  const listaAnexos = container.querySelector('.chat-anexos-pendentes');
  const dock = container;

  function autoAltura() {
    area.style.height = 'auto';
    area.style.height = Math.min(140, area.scrollHeight) + 'px';
  }
  area.addEventListener('input', autoAltura);

  function pintarBotaoEnviar() {
    const respondendo = ctx.estaRespondendo();
    btnEnviar.innerHTML = respondendo ? iconeParar() : iconeEnviar();
    btnEnviar.classList.toggle('tut-send-parar', respondendo);
    btnEnviar.setAttribute('aria-label', respondendo ? 'Parar geração' : 'Enviar');
  }
  pintarBotaoEnviar();

  function renderizarAnexosPendentes() {
    listaAnexos.hidden = anexosPendentes.length === 0;
    listaAnexos.innerHTML = anexosPendentes.map(function (a, i) {
      return '<span class="chat-anexo-chip pendente"><svg class="ic"><use href="#i-doc"/></svg>' + a.nome +
        '<button type="button" data-remover-anexo="' + i + '" aria-label="Remover anexo">✕</button></span>';
    }).join('');
  }
  listaAnexos.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-remover-anexo]');
    if (!btn) return;
    anexosPendentes.splice(Number(btn.dataset.removerAnexo), 1);
    renderizarAnexosPendentes();
  });

  function anexarArquivos(files) {
    Array.prototype.forEach.call(files, function (f) {
      anexosPendentes.push({ nome: f.name, tamanho: f.size });
    });
    renderizarAnexosPendentes();
  }

  function enviar() {
    if (ctx.estaRespondendo()) { ctx.aoParar(); return; }
    const texto = area.value.trim();
    if (!texto && anexosPendentes.length === 0) return;
    ctx.aoEnviar(texto, anexosPendentes);
    anexosPendentes = [];
    renderizarAnexosPendentes();
    area.value = '';
    autoAltura();
  }

  btnEnviar.addEventListener('click', enviar);
  area.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); }
    if (e.key === 'Escape' && ctx.estaRespondendo()) { e.preventDefault(); ctx.aoParar(); }
  });

  container.querySelectorAll('[data-rapida]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (ctx.estaRespondendo()) return;
      ctx.aoEnviar(b.dataset.rapida, []);
    });
  });

  btnAnexar.addEventListener('click', function () { inputArquivo.click(); });
  inputArquivo.addEventListener('change', function () {
    anexarArquivos(this.files);
    this.value = '';
  });

  // Arrastar-e-soltar em qualquer ponto do dock, nao so num botao.
  ['dragover', 'dragenter'].forEach(function (ev) {
    dock.addEventListener(ev, function (e) { e.preventDefault(); dock.classList.add('chat-dock-drag'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    dock.addEventListener(ev, function () { dock.classList.remove('chat-dock-drag'); });
  });
  dock.addEventListener('drop', function (e) {
    e.preventDefault();
    if (e.dataTransfer && e.dataTransfer.files.length) anexarArquivos(e.dataTransfer.files);
  });

  return {
    focar: function () { area.focus(); },
    anexarArquivos: anexarArquivos,
    atualizarEstadoBotao: pintarBotaoEnviar,
  };
}
