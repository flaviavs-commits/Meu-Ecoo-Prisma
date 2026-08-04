# E14 - Painel operacional do superadmin

> **Status:** AGUARDANDO DECISÃO · **Responsavel:** Analizar o front do Prisma
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

## 4. Diario de execucao

- [2026-08-03] Etapa aberta por Analizar o front do Prisma - o usuario escolheu tratar tier como perfil ALUNO/PROFESSOR/DIRETOR e autorizou troca irrestrita pelo superadmin; validacao: E11 e o codigo existente foram lidos antes da implementacao.
- [2026-08-03] Criado o núcleo do painel em `painel_admin/` com dashboard, listagem/busca, detalhe e troca de perfil auditada - por que: entregar a primeira fatia sem duplicar o Django Admin; como validei: `pytest painel_admin/tests/test_painel_superadmin.py -q` retornou `4 passed` e `manage.py check` retornou `0 silenced` em SQLite local. Estado: falta ampliar registros, operações destrutivas e validação Railway.
- [2026-08-03] Primeira fatia concluída localmente - por que: o núcleo seguro de troca de perfil está entregue; como validei: testes e check passaram. Estado final: **AGUARDANDO DECISÃO** para priorizar a próxima fatia (registros do backend, logs operacionais e ações destrutivas auditadas) e autorizar a validação/deploy Railway.
- [2026-08-03] Deploy automático ativado no serviço Railway `api` - por que: o usuário pediu publicação por push; como validei: `railway status --json` mostrou fonte `flaviavs-commits/Meu-Ecoo-Prisma`, branch `main`, root `backend` e deployment do commit `4a5b593`. Estado: o gatilho está ativo, mas a assinatura vencida pode impedir a conclusão do deployment.
- [2026-08-03] Health check preparado para Gunicorn no Railway - por que: o health check interno chega por HTTP e o redirect global para HTTPS impedia a réplica de ficar saudável; como validei: testes backend retornaram `7 passed`, `manage.py check` sem issues e Gunicorn local respondeu HTTP 200 em `/api/v1/health/`. Estado final: **AGUARDANDO DECISÃO** para ampliar o painel; a validação final do novo deployment depende do push e da disponibilidade operacional do Railway.
- [2026-08-03] Validação Railway bloqueada - por que: após o push `53e66b2`, três tentativas com Gunicorn e uma comparação com `runserver` construíram a imagem, mas terminaram com `1/1 replicas never became healthy`, sem traceback da aplicação; como validei: logs de build do Railway e health check público HTTP 200 na réplica anterior. O dashboard informa assinatura vencida. Estado final: **BLOQUEADO** até regularizar a assinatura/infraestrutura; a configuração de produção foi restaurada para Gunicorn.

## 5. Criterio de pronto da primeira fatia

- [ ] testes TDD de acesso, troca de perfil, validação e auditoria;
- [ ] painel protegido contra usuario comum e staff não-superuser;
- [ ] `manage.py check` e suíte do painel passando;
- [ ] documentação e estado atual atualizados;
- [x] bloqueio operacional do deploy Railway registrado; validação final está **BLOQUEADA** pela assinatura/infraestrutura.
