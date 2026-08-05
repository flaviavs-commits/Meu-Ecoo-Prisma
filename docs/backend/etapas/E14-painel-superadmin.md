# E14 - Painel operacional do superadmin

> **Status:** CONCLUÍDA (1ª a 4ª fatia) · **Responsavel:** Code Review
> **Depende de:** E04, E11 · **Destrava:** operacao interna do backend

## 1. Objetivo

Adicionar um painel web interno para o superadmin acompanhar e operar o
backend do Prisma, inspirado no painel do projeto Vs, sem criar um segundo
servico Railway ou duplicar banco/API.

## 2. Decisoes

- O painel sera um app Django no mesmo servico do backend, em `/painel/`.
- O painel é exclusivo para contas ativas com `is_superuser=True`, perfil
  `MANTENEDOR` e vínculo com a instituição mantenedora `VITIS_SOULS`.
- O tier de controle é separado dos perfis acadêmicos: `MANTENEDOR` administra
  a plataforma; `ALUNO`, `PROFESSOR` e `DIRETOR` usam as telas acadêmicas.
- O mantenedor pode trocar perfis acadêmicos com motivo obrigatório e auditoria.
  O perfil `MANTENEDOR` só pode existir em um superadmin da Vitis Souls.
- O painel nao exibira conversa crua de aluno, senha, token ou segredo.
- Exclusao fisica nao sera oferecida nesta primeira fatia; desativacao auditada
  e o comportamento seguro ja definido pela E11.

## 3. Primeira fatia

- dashboard com contagens de usuarios, instituicoes e auditoria recente;
- lista e busca de usuarios;
- detalhe de usuario sem dados sensiveis;
- troca de perfil com motivo e auditoria;
- links para os registros somente leitura do Django Admin.

## 3.1 Segunda fatia (concluída em 2026-08-05)

- `/painel/registros/`: lista paginada de `RegistroDeAuditoria`, com filtro por
  ação e busca por ator/objeto/motivo;
- `/painel/usuarios/<pk>/zerar-creditos/`: ação destrutiva que zera o saldo de
  créditos alocado a um usuário (reusa `creditos.reduzir_alocacao`), exige
  confirmação + motivo, fica auditada (`painel_admin/services/zerar_creditos.py`);
- `/painel/usuarios/<pk>/desativar/`: ação destrutiva que remove o acesso do
  usuário à instituição (reusa `contas.desativar_usuario` da E11), exige
  confirmação + motivo, fica auditada;
- tela de usuário passa a mostrar o saldo de créditos e os dois botões
  destrutivos, cada um com confirmação client-side (`confirm()`) além da
  confirmação server-side obrigatória.

## 3.2 Terceira fatia (concluída em 2026-08-05)

- `/painel/instituicoes/`: criação de instituição com documento único e
  crédito inicial opcional no ledger append-only;
- `/painel/contas-teste/`: criação de contas acadêmicas ativas para os perfis
  `ALUNO`, `PROFESSOR` e `DIRETOR`, sempre vinculadas a uma instituição ativa;
- criação de instituições e contas de teste protegida por superadmin, com
  transação, validação de senha e registro em `RegistroDeAuditoria`;
- contas de teste recebem explicitamente `is_staff=False` e
  `is_superuser=False`, para que o fluxo de controle não seja confundido com
  as telas acadêmicas do produto.

## 3.3 Quarta fatia — tier mantenedor e governança cross-tenant (concluída em 2026-08-05)

- `Instituicao` ganhou o tipo `MANTENEDORA` e o código estável `VITIS_SOULS`.
  A Vitis Souls não exige CPF/CNPJ; escolas continuam exigindo documento.
- A migração `0007_mantenedora_vitis_souls` cria a Vitis Souls quando
  necessário e vincula a ela os superusuários existentes com o perfil
  `MANTENEDOR`.
- O acesso cross-tenant exige simultaneamente conta ativa, superusuário,
  perfil `MANTENEDOR` e vínculo com a Vitis Souls. `is_staff` isoladamente não
  concede esse poder.
- O painel permite abrir, editar e arquivar instituições escolares, editar
  contas de outras instituições e administrar as ações já existentes de
  perfil, créditos e acesso. Cada alteração relevante exige motivo e auditoria.
- Arquivar uma escola desativa suas contas e preserva os registros. O Admin
  completo também não oferece exclusão física de instituições ou usuários;
  Vitis Souls fica protegida contra alteração por esse fluxo.
- Contas acadêmicas não podem ser criadas na Vitis Souls e contas de teste não
  podem receber o tier `MANTENEDOR`.

## 4. Diario de execucao

- [2026-08-03] Etapa aberta por Analizar o front do Prisma - o usuario escolheu tratar tier como perfil ALUNO/PROFESSOR/DIRETOR e autorizou troca irrestrita pelo superadmin; validacao: E11 e o codigo existente foram lidos antes da implementacao.
- [2026-08-03] Criado o núcleo do painel em `painel_admin/` com dashboard, listagem/busca, detalhe e troca de perfil auditada - por que: entregar a primeira fatia sem duplicar o Django Admin; como validei: `pytest painel_admin/tests/test_painel_superadmin.py -q` retornou `4 passed` e `manage.py check` retornou `0 silenced` em SQLite local. Estado: falta ampliar registros, operações destrutivas e validação Railway.
- [2026-08-03] Primeira fatia concluída localmente - por que: o núcleo seguro de troca de perfil está entregue; como validei: testes e check passaram. Estado final: **AGUARDANDO DECISÃO** para priorizar a próxima fatia (registros do backend, logs operacionais e ações destrutivas auditadas) e autorizar a validação/deploy Railway.
- [2026-08-03] Deploy automático ativado no serviço Railway `api` - por que: o usuário pediu publicação por push; como validei: `railway status --json` mostrou fonte `flaviavs-commits/Meu-Ecoo-Prisma`, branch `main`, root `backend` e deployment do commit `4a5b593`. Estado: o gatilho está ativo, mas a assinatura vencida pode impedir a conclusão do deployment.
- [2026-08-03] Health check preparado para Gunicorn no Railway - por que: o health check interno chega por HTTP e o redirect global para HTTPS impedia a réplica de ficar saudável; como validei: testes backend retornaram `7 passed`, `manage.py check` sem issues e Gunicorn local respondeu HTTP 200 em `/api/v1/health/`. Estado final: **AGUARDANDO DECISÃO** para ampliar o painel; a validação final do novo deployment depende do push e da disponibilidade operacional do Railway.
- [2026-08-03] Validação Railway bloqueada - por que: após o push `53e66b2`, três tentativas com Gunicorn e uma comparação com `runserver` construíram a imagem, mas terminaram com `1/1 replicas never became healthy`, sem traceback da aplicação; como validei: logs de build do Railway e health check público HTTP 200 na réplica anterior. O dashboard informa assinatura vencida. Estado final: **BLOQUEADO** até regularizar a assinatura/infraestrutura; a configuração de produção foi restaurada para Gunicorn.
- [2026-08-05] Painel do prisma fechou a 1ª fatia e entregou a 2ª (registros de auditoria + ações destrutivas auditadas: zerar créditos e desativar usuário) - por que: o usuário autorizou finalizar a etapa de ponta a ponta, com a assinatura Railway já regularizada; como validei: reforcei o checklist da 1ª fatia com 2 testes novos (staff não-superuser, perfil inválido) e criei 11 testes novos para a 2ª fatia; suíte completa do backend em `116 passed, 1 skipped` e `manage.py check` sem issues. Commit `2aaca78` na `main` (branch de trabalho mesclada e apagada, junto com a branch obsoleta `agent/publica-design-backend`, cujo conteúdo já estava superado pela `main`).
- [2026-08-05] Deploy Railway destravado - por que: a assinatura foi regularizada e o deploy automático do commit `2aaca78` falhou de novo com `1/1 replicas never became healthy`; investigando via `railway` CLI, identifiquei que `DJANGO_ALLOWED_HOSTS` só tinha o domínio público, e o healthcheck interno do Railway bate no container por um Host diferente, causando `DisallowedHost` (400) tratado como "service unavailable"; como validei: ampliei `DJANGO_ALLOWED_HOSTS` (domínio público + `api.railway.internal` + `healthcheck.railway.app` + loopback + `*.up.railway.app`) via `railway variable set`, rodei `railway redeploy --from-source`, e o deploy ficou `Online` com `GET /api/v1/health/` retornando 200 e `GET /painel/` retornando 302 (login) em produção. Estado final: **CONCLUÍDA** — 1ª e 2ª fatia entregues, testadas e publicadas em produção. Próxima fatia (se houver) fica para uma nova etapa/decisão.
- [2026-08-05] Quarta fatia concluída por Code Review - por que: a operação precisava separar o controle técnico da experiência acadêmica e permitir que a equipe Vitis Souls administrasse as instituições sem documento fiscal próprio; como implementei: criei o tipo `MANTENEDORA`, o código reservado `VITIS_SOULS`, o perfil `MANTENEDOR`, a migração de superadmins existentes, guardas de autorização cross-tenant, edição/arquivamento no painel e proteção contra exclusão física; como validei: `manage.py check`, `makemigrations --check --dry-run`, suíte focada com `45 passed` e suíte completa com `157 passed, 2 skipped`. Estado final: **CONCLUÍDA localmente; aguardando publicação automática e validação remota do deployment**.

## 5. Criterio de pronto da primeira fatia

- [x] testes TDD de acesso, troca de perfil, validação e auditoria;
- [x] painel protegido contra usuario comum e staff não-superuser;
- [x] `manage.py check` e suíte do painel passando;
- [x] documentação e estado atual atualizados;
- [x] bloqueio operacional do deploy Railway resolvido; deploy validado em produção (2026-08-05).

## 6. Criterio de pronto da segunda fatia

- [x] registros/logs operacionais visíveis e filtráveis no painel;
- [x] ações destrutivas (zerar créditos, remover da instituição) com confirmação + motivo + auditoria;
- [x] suíte completa do backend passando (`116 passed, 1 skipped`);
- [x] publicado e validado em produção no Railway.

## 7. Critério de pronto da terceira fatia

- [x] superadmin consegue abrir o formulário de instituições;
- [x] superadmin consegue abrir o formulário de contas de teste;
- [x] documento e e-mail duplicados são rejeitados sem duplicação;
- [x] senha e perfis acadêmicos são validados;
- [x] ledger inicial e auditoria são gravados na mesma transação;
- [x] contas de teste não recebem flags de staff ou superuser;
- [x] validação automatizada local concluída; deploy remoto fica pendente de
  autorização operacional.

**Estado final:** CONCLUÍDA localmente no commit `2a45e81`; aguardando apenas
deploy e teste manual autenticado. Identidade: **Code Review**.

## 8. Critério de pronto da quarta fatia

- [x] Vitis Souls é criada sem CPF/CNPJ e identificada por código estável;
- [x] superadmins existentes são vinculados ao tier `MANTENEDOR` por migração;
- [x] contas ativas sem o vínculo correto não entram no painel cross-tenant;
- [x] instituições e usuários escolares podem ser editados pelo mantenedor;
- [x] arquivamento desativa acesso, preserva dados e registra auditoria;
- [x] exclusão física foi removida do Admin para instituições e usuários;
- [x] contas acadêmicas não entram na Vitis Souls;
- [x] validação automatizada local concluída.

**Estado final:** CONCLUÍDA localmente; publicação automática e validação
remota ficam registradas após o push. Identidade: **Code Review**.

## 9. Publicação da terceira fatia

Em 2026-08-05, os commits `2a45e81` e `7aaaa11` foram publicados em
`origin/main`. O deployment Railway `75ac6e3d-2ba6-414b-afdc-07a6803e69c3`
terminou com `SUCCESS`. As duas novas rotas foram verificadas externamente:
ambas retornam `302` para autenticação sem sessão; o health check retorna
`200`.

**Estado final:** CONCLUÍDA e publicada; aguardando somente teste manual
autenticado. Identidade: **Code Review**.

## 10. Publicação da quarta fatia

O push do commit `fff2459` acionou o deploy automático do Railway. O
deployment `9688809f-6d83-4465-bbf0-dd15118661d8` terminou com `SUCCESS` e
executou a migração predeploy `python manage.py migrate --noinput`.

Validação pública observada: health da API em `200`; `/painel/`,
`/painel/instituicoes/`, `/painel/contas-teste/` e `/painel/usuarios/` em `302`
sem sessão; `/backoffice/login/` em `200`; proxy Vercel do painel em `302` e
proxy Vercel do health em `200`.

**Estado final:** CONCLUÍDA e publicada; aguardando apenas teste manual
autenticado sem reutilizar credenciais expostas. Identidade: **Code Review**.

## 12. Correções da revisão (2026-08-05)

A revisão de `docs/REVISAO-2026-08-05-COMMITS-DO-DIA.md` apontou quatro
problemas no painel, todos corrigidos:

- **Arquivamento irreversível (achado 10).** O `update()` em massa desativava
  todas as contas sem registrar quais estavam ativas. Agora cada conta atingida
  gera seu próprio `RegistroDeAuditoria`, e `desarquivar_instituicao` reativa
  exatamente o conjunto do último arquivamento — não volta quem foi desativado
  individualmente entre ciclos, nem quem foi transferido de escola. Nova rota
  `painel-instituicao-desarquivar`.
- **Listas truncadas em 100 (achado 9).** `instituicoes` e `usuarios` agora
  paginam em 25, com contagem total visível.
- **`DISTINCT` na auditoria (achado 16).** O filtro de ações virou a constante
  `ACOES_AUDITADAS`, em vez de varrer a tabela a cada carga da página.
- **Ordem dos decoradores (sugestão 18).** `@superadmin_required` passou a vir
  antes de `@require_POST` nas 6 rotas destrutivas, para que um `GET` anônimo
  vá ao login em vez de receber `405` confirmando a rota.

Validação: SQLite `231 passed, 3 skipped`; PostgreSQL `234 passed`;
`manage.py check` e `makemigrations --check --dry-run` limpos.

## 11. Redeploy final

O commit documental `0ed484a` acionou o redeploy automático final
`4af56ba7-4c3a-466b-86b0-2ad2e03aad7a`, concluído com `SUCCESS`. A nova
checagem confirmou API health `200`, painel e subrotas em `302` sem sessão,
`/backoffice/login/` em `200`, proxy Vercel do painel em `302` e proxy Vercel
do health em `200`.

**Estado final:** CONCLUÍDA e publicada; aguardando apenas teste manual
autenticado sem reutilizar credenciais expostas. Identidade: **Code Review**.
