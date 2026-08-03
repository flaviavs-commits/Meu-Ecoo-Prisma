/* Motor de traducao: 5 idiomas via dicionario JSON + atributos data-i18n*.
   Sem dependencia externa - fetch dos JSON em assets/i18n/<codigo>.json.

   Convencoes nos elementos:
     data-i18n="chave"            troca o textContent
     data-i18n-html="chave"       troca o innerHTML (chave com marcacao,
                                   ex.: "<u>...</u>" ou entidade &nbsp;)
     data-i18n-attr="a:k;b:k2"    troca um ou mais atributos (par
                                   atributo:chave, separados por ;)

   Nao traduz dado de demonstracao (nomes, textos de conversa do tutor,
   datas especificas) - so strings de interface, por decisao registrada
   no IA.md: sao o "roteiro" da demo, nao parte da UI. */
(function () {
  var CHAVE_LS = 'prisma-lang';
  var PADRAO = 'pt-BR';
  var IDIOMAS = ['pt-BR', 'en', 'es', 'fr', 'de'];
  var cache = {};

  function idiomaAtual() {
    try {
      var salvo = localStorage.getItem(CHAVE_LS);
      if (salvo && IDIOMAS.indexOf(salvo) !== -1) return salvo;
    } catch (e) {}
    return PADRAO;
  }

  function carregar(codigo) {
    if (cache[codigo]) return Promise.resolve(cache[codigo]);
    return fetch('assets/i18n/' + codigo + '.json')
      .then(function (r) {
        if (!r.ok) throw new Error('dicionario nao encontrado: ' + codigo);
        return r.json();
      })
      .then(function (dic) {
        cache[codigo] = dic;
        return dic;
      });
  }

  var dicionarioAtual = null;

  function aplicarNoElemento(el, dic) {
    if (el.hasAttribute('data-i18n')) {
      var chave = el.getAttribute('data-i18n');
      if (dic[chave] !== undefined) el.textContent = dic[chave];
    }
    if (el.hasAttribute('data-i18n-html')) {
      var chaveH = el.getAttribute('data-i18n-html');
      if (dic[chaveH] !== undefined) el.innerHTML = dic[chaveH];
    }
    if (el.hasAttribute('data-i18n-attr')) {
      var spec = el.getAttribute('data-i18n-attr');
      spec.split(';').forEach(function (par) {
        var partes = par.split(':');
        var attr = partes[0], chaveA = partes[1];
        if (attr && chaveA && dic[chaveA] !== undefined) {
          el.setAttribute(attr, dic[chaveA]);
        }
      });
    }
  }

  function aplicar(dic) {
    dicionarioAtual = dic;
    document.querySelectorAll('[data-i18n]').forEach(function (el) { aplicarNoElemento(el, dic); });
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) { aplicarNoElemento(el, dic); });
    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) { aplicarNoElemento(el, dic); });
  }

  // Para conteudo criado depois da carga inicial (ex.: o rotulo de
  // ordenacao e o contador de materiais em app.js, que trocam de chave
  // em resposta a um clique) - reaplica so nesse elemento, sem varrer a
  // pagina inteira de novo.
  function aplicarEm(el) {
    if (dicionarioAtual) aplicarNoElemento(el, dicionarioAtual);
  }

  function marcarSelecionado(codigo) {
    document.querySelectorAll('.lang-opt').forEach(function (btn) {
      btn.classList.toggle('on', btn.dataset.lang === codigo);
    });
    document.documentElement.lang = codigo;
  }

  function fecharSeletor() {
    var seletor = document.getElementById('dd-lang');
    var fundo = document.getElementById('dd-backdrop');
    if (seletor) seletor.classList.remove('open');
    if (fundo) fundo.classList.remove('open');
  }

  function setLang(codigo) {
    if (IDIOMAS.indexOf(codigo) === -1) return;
    carregar(codigo).then(function (dic) {
      aplicar(dic);
      marcarSelecionado(codigo);
      fecharSeletor();
      try { localStorage.setItem(CHAVE_LS, codigo); } catch (e) {}
    }).catch(function (err) {
      console.error('[i18n] falha ao trocar para', codigo, err);
    });
  }

  // API publica, usada pelo app.js ao clicar num item do seletor e para
  // reaplicar traducao em conteudo dinamico (contador, rotulo de ordenacao)
  window.PrismaI18n = { setLang: setLang, idiomaAtual: idiomaAtual, aplicarEm: aplicarEm };

  // Carrega o idioma salvo (ou pt-BR) assim que o DOM estiver pronto -
  // os textos em portugues ja estao no HTML como fallback, entao uma
  // falha de rede aqui degrada para "pagina em portugues", nao quebra.
  document.addEventListener('DOMContentLoaded', function () {
    setLang(idiomaAtual());
  });
})();
