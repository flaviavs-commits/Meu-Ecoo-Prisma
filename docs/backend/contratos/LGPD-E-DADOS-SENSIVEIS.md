# Contrato: LGPD e dados sensiveis

> **Ha menores de idade na base.** O produto e vendido a escolas de ensino
> fundamental e medio, alem de universidades. Isso muda o tratamento de dado
> pessoal de "boa pratica" para "obrigacao legal".
>
> Toda etapa que toca dado de pessoa respeita este contrato.

**Estado do contrato (2026-08-03):** vigente para desenvolvimento; a
validacao juridica da base legal, do fluxo de consentimento e dos prazos de
retencao continua pendente antes de producao. Estado pendente e bloqueio de
capacidade, nao autorizacao implicita para processar o dado.

## 1. O que a lei exige aqui, em uma frase

A LGPD (Lei 13.709/2018) trata dado de crianca e adolescente em artigo proprio
(art. 14): o tratamento deve ser feito **no melhor interesse do titular**, e o
dado de crianca exige **consentimento especifico de pelo menos um dos pais ou do
responsavel legal**.

> Este documento e orientacao tecnica de engenharia, nao parecer juridico. As
> decisoes de politica de privacidade, base legal e prazo de retencao precisam
> de validacao juridica antes de producao. **Registre isso como pendencia, nao
> como resolvido.**

## 2. Quem consente, no modelo institucional

O produto e B2B: a **escola** contrata e cadastra os usuarios; o aluno nao se
cadastra sozinho. Isso muda quem opera o consentimento, mas **nao elimina** a
exigencia dele.

Consequencia pratica para o backend:

- o `Usuario` precisa registrar `data_nascimento` - sem isso o sistema nao sabe
  quem e menor;
- para menor, precisa existir registro de **quem** consentiu, **quando** e por
  qual meio, ainda que o consentimento seja coletado pela escola fora do
  sistema;
- a ausencia desse registro nao pode ser silenciosa: e um estado visivel
  (pendente), nao um campo nulo que ninguem olha.

Campos minimos no `Usuario` ([E02](../etapas/E02-nucleo-de-dados-e-multitenancy.md)):

| Campo | Papel |
|-------|-------|
| `data_nascimento` | Define se e menor. Obrigatorio para aluno. |
| `responsavel_nome` | Preenchido quando menor |
| `responsavel_contato` | Preenchido quando menor |
| `consentimento_responsavel_em` | Data/hora. Nulo = pendente, e isso e visivel |

## 3. Classificacao dos dados que o sistema guarda

| Categoria | Exemplos | Tratamento |
|-----------|----------|------------|
| **Identificacao** | nome, e-mail, data de nascimento, responsavel | Acesso restrito ao perfil que precisa. Nunca em log. |
| **Educacional** | notas, faltas, desempenho | Dado de aprendizagem de menor. Restrito ao aluno, seus professores e a direcao. |
| **Conversa com o tutor** | mensagens do aluno com a IA | **O mais sensivel do sistema.** Ver item 4. |
| **Credencial** | senha | Hash forte do Django (Argon2/PBKDF2). Nunca reversivel, nunca em log. |
| **Operacional** | creditos, uso de IA | Nao e pessoal em si, mas ligado a pessoa. |

## 4. Conversa do tutor - o ponto mais delicado

Um adolescente conversando com um tutor de IA sobre o que nao entende revela
dificuldade de aprendizagem, e as vezes muito mais que isso. O log bruto dessa
conversa e persistido (decisao registrada na [visao geral](../VISAO-GERAL.md)).

Regras nao negociaveis:

1. **Professor e diretor nao leem a conversa crua do aluno por padrao.** O que
   sobe para eles e agregado ou consolidado. Qualquer acesso individual precisa
   de justificativa e trilha de auditoria.
2. A conversa **nunca** sai em log de aplicacao, mensagem de erro ou telemetria.
3. Prazo de retencao do bruto precisa ser definido - hoje e **pendencia
   aberta**. Ver [E07](../etapas/E07-memoria-e-conversas.md).
4. O conteudo enviado ao provedor de IA e dado de menor saindo do sistema. O
   gateway ([E06](../etapas/E06-gateway-de-ia.md)) e o unico ponto por onde
   isso pode acontecer, justamente para ser auditavel.

## 5. Minimizacao - a defesa mais barata

Dado que nao existe nao vaza, nao precisa de consentimento e nao precisa ser
protegido.

- **Nao colete o que nao usa.** Se um campo nao tem consumidor claro no produto,
  ele nao entra no model. CPF de aluno, endereco e telefone pessoal entram
  **so** se houver necessidade demonstrada.
- **Nao serialize o model inteiro por conveniencia.** Cada endpoint responde os
  campos que aquela tela precisa - ver
  [API-CONVENCOES](API-CONVENCOES.md), item 10.
- **Nao registre dado pessoal em log.** Log identifica por id, nunca por nome ou
  e-mail.

## 6. Direitos do titular

A lei da ao titular (ou ao responsavel, no caso do menor) direito de acesso,
correcao, portabilidade e eliminacao. O backend nao precisa de tela para isso
nesta fase, mas precisa **ser capaz** de atender:

- todo dado pessoal e alcancavel a partir do `Usuario` por FK - sem dado orfao
  em tabela solta;
- exclusao e **anonimizacao** quando o registro nao pode sumir (uma nota lancada
  faz parte do historico academico da escola) - substituir identificacao por
  marcador, preservando o registro academico.

Implementar isso e etapa futura. **Nao modelar de um jeito que impeça** e
obrigacao de agora.

## 7. Checklist para qualquer etapa que toque dado de pessoa

- [ ] Nenhum campo novo foi criado sem uso claro no produto
- [ ] Nenhum dado pessoal aparece em log, erro ou telemetria
- [ ] O endpoint responde so os campos que a tela precisa
- [ ] Acesso e restrito por perfil **e** por instituicao
- [ ] Se o dado e de menor, ha registro de consentimento (ou estado pendente visivel)
- [ ] Senha nunca sai, nunca e logada, nunca e comparada em texto puro
- [ ] O dado consegue ser localizado e anonimizado a partir do `Usuario`

Ao concluir uma etapa, o agente deve registrar no diario dela quais itens foram
validados, quais nao se aplicam e quais ficaram pendentes, com o comando e a
saida observada. Nenhuma etapa pode marcar este contrato como cumprido se a
validacao juridica ou a retencao aplicavel ainda estiverem abertas.
