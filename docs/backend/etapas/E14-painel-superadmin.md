# E14 - Painel operacional do superadmin

> **Status:** CONCLUÍDA (1ª e 2ª fatia) · **Responsavel:** Painel do prisma
> **Depende de:** E04, E11 · **Destrava:** operacao interna do backend

## 1. Objetivo

Adicionar um painel web interno para o superadmin acompanhar e operar o
backend do Prisma, inspirado no painel do projeto Vs, sem criar um segundo
servico Railway ou duplicar banco/API.

## 2. Decisoes

- O painel sera um app Django no mesmo servico do backend, em `/painel/`.
- O acesso inicial sera exclusivo para `is_superuser`; `is_staff` continua
  suficiente apenas para o Django Admin existente.
- "Tier" significa o campo `perfil` atual: `ALUNO`, `PROFESSOR` ou `DIRETOR`.
- O superadmin pode trocar o perfil sempre que quiser. A troca exige motivo e
  fica registrada em `RegistroDeAuditoria`.
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

## 4. Diario de execucao

- [2026-08-03] Etapa aberta por Analizar o front do Prisma - o usuario escolheu tratar tier como perfil ALUNO/PROFESSOR/DIRETOR e autorizou troca irrestrita pelo superadmin; validacao: E11 e o codigo existente foram lidos antes da implementacao.
- [2026-08-03] Criado o núcleo do painel em `painel_admin/` com dashboard, listagem/busca, detalhe e troca de perfil auditada - por que: entregar a primeira fatia sem duplicar o Django Admin; como validei: `pytest painel_admin/tests/test_painel_superadmin.py -q` retornou `4 passed` e `manage.py check` retornou `0 silenced` em SQLite local. Estado: falta ampliar registros, operações destrutivas e validação Railway.
- [2026-08-03] Primeira fatia concluída localmente - por que: o núcleo seguro de troca de perfil está entregue; como validei: testes e check passaram. Estado final: **AGUARDANDO DECISÃO** para priorizar a próxima fatia (registros do backend, logs operacionais e ações destrutivas auditadas) e autorizar a validação/deploy Railway.
- [2026-08-03] Deploy automático ativado no serviço Railway `api` - por que: o usuário pediu publicação por push; como validei: `railway status --json` mostrou fonte `flaviavs-commits/Meu-Ecoo-Prisma`, branch `main`, root `backend` e deployment do commit `4a5b593`. Estado: o gatilho está ativo, mas a assinatura vencida pode impedir a conclusão do deployment.
- [2026-08-03] Health check preparado para Gunicorn no Railway - por que: o health check interno chega por HTTP e o redirect global para HTTPS impedia a réplica de ficar saudável; como validei: testes backend retornaram `7 passed`, `manage.py check` sem issues e Gunicorn local respondeu HTTP 200 em `/api/v1/health/`. Estado final: **AGUARDANDO DECISÃO** para ampliar o painel; a validação final do novo deployment depende do push e da disponibilidade operacional do Railway.
- [2026-08-03] Validação Railway bloqueada - por que: após o push `53e66b2`, três tentativas com Gunicorn e uma comparação com `runserver` construíram a imagem, mas terminaram com `1/1 replicas never became healthy`, sem traceback da aplicação; como validei: logs de build do Railway e health check público HTTP 200 na réplica anterior. O dashboard informa assinatura vencida. Estado final: **BLOQUEADO** até regularizar a assinatura/infraestrutura; a configuração de produção foi restaurada para Gunicorn.
- [2026-08-05] Painel do prisma fechou a 1ª fatia e entregou a 2ª (registros de auditoria + ações destrutivas auditadas: zerar créditos e desativar usuário) - por que: o usuário autorizou finalizar a etapa de ponta a ponta, com a assinatura Railway já regularizada; como validei: reforcei o checklist da 1ª fatia com 2 testes novos (staff não-superuser, perfil inválido) e criei 11 testes novos para a 2ª fatia; suíte completa do backend em `116 passed, 1 skipped` e `manage.py check` sem issues. Commit `2aaca78` na `main` (branch de trabalho mesclada e apagada, junto com a branch obsoleta `agent/publica-design-backend`, cujo conteúdo já estava superado pela `main`).
- [2026-08-05] Deploy Railway destravado - por que: a assinatura foi regularizada e o deploy automático do commit `2aaca78` falhou de novo com `1/1 replicas never became healthy`; investigando via `railway` CLI, identifiquei que `DJANGO_ALLOWED_HOSTS` só tinha o domínio público, e o healthcheck interno do Railway bate no container por um Host diferente, causando `DisallowedHost` (400) tratado como "service unavailable"; como validei: ampliei `DJANGO_ALLOWED_HOSTS` (domínio público + `api.railway.internal` + `healthcheck.railway.app` + loopback + `*.up.railway.app`) via `railway variable set`, rodei `railway redeploy --from-source`, e o deploy ficou `Online` com `GET /api/v1/health/` retornando 200 e `GET /painel/` retornando 302 (login) em produção. Estado final: **CONCLUÍDA** — 1ª e 2ª fatia entregues, testadas e publicadas em produção. Próxima fatia (se houver) fica para uma nova etapa/decisão.

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

**Estado final:** CONCLUÍDA localmente no commit `3bd40f0`; aguardando apenas
deploy e teste manual autenticado. Identidade: **Code Review**.
