/* Motor de dialogos: abre/fecha, empilha, prende foco, ESC, trava scroll.
   Cada modal do projeto (settings, confirmacao, etc.) nasce daqui - eles
   descrevem CONTEUDO, este arquivo garante que todos se comportam do
   mesmo jeito (Linear/Notion/Stripe: nunca um modal "diferente" no meio
   dos outros). Sem framework: DOM puro, pensado para o mockup estatico. */

const pilha = [];
let travasScroll = 0;
let scrollY = 0;

function travarScroll() {
  if (travasScroll === 0) {
    scrollY = window.scrollY;
    document.body.style.position = 'fixed';
    document.body.style.top = '-' + scrollY + 'px';
    document.body.style.left = '0';
    document.body.style.right = '0';
  }
  travasScroll++;
}

function destravarScroll() {
  travasScroll = Math.max(0, travasScroll - 1);
  if (travasScroll === 0) {
    document.body.style.position = '';
    document.body.style.top = '';
    document.body.style.left = '';
    document.body.style.right = '';
    window.scrollTo(0, scrollY);
  }
}

function focaveisEm(raiz) {
  const sel = 'a[href],button:not([disabled]),textarea:not([disabled]),input:not([disabled]),select:not([disabled]),[tabindex]:not([tabindex="-1"])';
  return Array.prototype.slice.call(raiz.querySelectorAll(sel)).filter(function (el) {
    return el.offsetParent !== null || el === document.activeElement;
  });
}

function aoTeclar(e) {
  const topo = pilha[pilha.length - 1];
  if (!topo) return;
  if (e.key === 'Escape' && topo.fecharComEsc) {
    e.stopPropagation();
    topo.fechar('esc');
    return;
  }
  if (e.key === 'Tab') {
    const alvos = focaveisEm(topo.painel);
    if (!alvos.length) { e.preventDefault(); return; }
    const primeiro = alvos[0], ultimo = alvos[alvos.length - 1];
    if (e.shiftKey && document.activeElement === primeiro) {
      e.preventDefault(); ultimo.focus();
    } else if (!e.shiftKey && document.activeElement === ultimo) {
      e.preventDefault(); primeiro.focus();
    }
  }
}
document.addEventListener('keydown', aoTeclar, true);

/**
 * Abre um dialogo generico. Quem chama monta o conteudo do `.pm-dialog`
 * (header/body/footer) - este modulo so cuida do envelope (fundo, foco,
 * ESC, scroll, pilha, animacao).
 *
 * @param {{tamanho?:string, rotuloPor?:string, fecharComEsc?:boolean, fecharNoFundo?:boolean, aoFechar?:(motivo:string)=>void, classe?:string}} opcoes
 * @returns {{fundo:HTMLElement, painel:HTMLElement, fechar:(motivo?:string)=>void, definirCarregando:(v:boolean)=>void}}
 */
export function abrirDialogo(opcoes) {
  const o = opcoes || {};
  const retornoFoco = document.activeElement;

  const fundo = document.createElement('div');
  fundo.className = 'pm-fundo';
  fundo.style.zIndex = String(70 + pilha.length * 2);

  const painel = document.createElement('div');
  painel.className = 'pm-dialogo pm-tam-' + (o.tamanho || 'md') + (o.classe ? ' ' + o.classe : '');
  painel.setAttribute('role', 'dialog');
  painel.setAttribute('aria-modal', 'true');
  painel.tabIndex = -1;
  if (o.rotuloPor) painel.setAttribute('aria-labelledby', o.rotuloPor);
  painel.style.zIndex = String(71 + pilha.length * 2);

  document.body.appendChild(fundo);
  document.body.appendChild(painel);
  travarScroll();

  let fechado = false;
  function fechar(motivo) {
    if (fechado) return;
    fechado = true;
    const idx = pilha.indexOf(entrada);
    if (idx !== -1) pilha.splice(idx, 1);
    fundo.classList.add('pm-saindo');
    painel.classList.add('pm-saindo');
    destravarScroll();
    setTimeout(function () {
      fundo.remove();
      painel.remove();
    }, 180);
    if (retornoFoco && typeof retornoFoco.focus === 'function' && document.contains(retornoFoco)) {
      retornoFoco.focus();
    }
    if (o.aoFechar) o.aoFechar(motivo || 'programatico');
  }

  if (o.fecharNoFundo !== false) {
    fundo.addEventListener('click', function () { fechar('fundo'); });
  }

  function definirCarregando(v) {
    painel.classList.toggle('pm-carregando', !!v);
    painel.setAttribute('aria-busy', v ? 'true' : 'false');
  }

  const entrada = {
    fundo: fundo,
    painel: painel,
    fechar: fechar,
    fecharComEsc: o.fecharComEsc !== false,
  };
  pilha.push(entrada);

  // Um frame para o navegador registrar o estado inicial antes de animar.
  requestAnimationFrame(function () {
    fundo.classList.add('pm-aberto');
    painel.classList.add('pm-aberto');
    const alvo = painel.querySelector('[data-pm-foco-inicial]') || focaveisEm(painel)[0] || painel;
    alvo.focus();
  });

  return { fundo: fundo, painel: painel, fechar: fechar, definirCarregando: definirCarregando };
}

/** Verdadeiro se algum dialogo estiver aberto - util para outros modulos (ex.: dropdowns) nao brigarem com o modal. */
export function haDialogoAberto() {
  return pilha.length > 0;
}
