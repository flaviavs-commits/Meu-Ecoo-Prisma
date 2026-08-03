/* Ponte fina para o toast que ja existe em app.js (`window.PrismaToast`,
   exposto de proposito para o sistema de modal reusar o mesmo host visual
   em vez de duplicar a logica de "avisozinho flutuante"). Fallback local
   so para o caso raro de app.js nao ter carregado ainda. */
export function avisar(texto, tipo) {
  if (typeof window.PrismaToast === 'function') {
    window.PrismaToast(texto, tipo);
    return;
  }
  console.info('[toast]', texto);
}
