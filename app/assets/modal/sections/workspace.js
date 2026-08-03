/* Secao "Instituição" (workspace, so diretor): identidade da escola
   dentro do Prisma - o que aparece para toda a equipe e alunos. */
export function montar(container) {
  container.innerHTML =
    '<div class="pm-section-head">' +
      '<p class="eyebrow">Espaço de trabalho</p>' +
      '<h2>Instituição</h2>' +
      '<p>Identidade da escola dentro do Prisma.</p>' +
    '</div>' +
    '<div class="pm-perfil-card">' +
      '<span class="pm-settings-av pm-perfil-av" style="background:#C79A2A">CH</span>' +
      '<div class="pm-perfil-quem"><b>Colégio Horizonte</b><span>horizonte.prisma.app</span></div>' +
      '<button type="button" class="btn btn-gho btn-sm" data-acao="logo">Alterar logo</button>' +
    '</div>' +
    '<div class="pm-grid-2">' +
      '<div class="field" style="margin:0"><label>Nome da instituição</label><input class="input" value="Colégio Horizonte"></div>' +
      '<div class="field" style="margin:0"><label>Subdomínio</label><input class="input" value="horizonte" style="text-align:right"></div>' +
      '<div class="field" style="margin:0;grid-column:1/-1"><label>Endereço</label><input class="input" value="Av. das Palmeiras, 480 — São Paulo, SP"></div>' +
      '<div class="field" style="margin:0"><label>CNPJ</label><input class="input" value="04.321.556/0001-90"></div>' +
      '<div class="field" style="margin:0"><label>Fuso horário</label><input class="input" value="América/São Paulo (GMT-3)"></div>' +
    '</div>' +
    '<div class="pm-acoes-dir"><button type="button" class="btn btn-pri" data-acao="salvar">Salvar alterações</button></div>' +
    '<div id="pm-ws-banner"></div>';

  container.querySelector('[data-acao="logo"]').addEventListener('click', function () {
    if (window.PrismaToast) window.PrismaToast('Envio de logo ainda não está disponível nesta demonstração.', 'aviso');
  });
  container.querySelector('[data-acao="salvar"]').addEventListener('click', function (e) {
    window.PrismaCarregando(e.currentTarget, 'Salvando…', 850, function () {
      if (window.PrismaToast) window.PrismaToast('Dados da instituição salvos', 'ok');
    });
  });
}
