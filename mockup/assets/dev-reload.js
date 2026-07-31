/* Live-reload de desenvolvimento: compara o Last-Modified da propria
   pagina a cada 2s e recarrega quando muda. So serve pra rodar local
   (python start_app.py / npm run dev) - remover antes de qualquer
   deploy publico. */
(function () {
  var lm = null;
  setInterval(function () {
    fetch(location.href, { method: 'HEAD', cache: 'no-store' })
      .then(function (r) {
        var v = r.headers.get('Last-Modified');
        if (lm && v && v !== lm) { location.reload(); }
        if (!lm) { lm = v; }
      })
      .catch(function () {});
  }, 2000);
})();
