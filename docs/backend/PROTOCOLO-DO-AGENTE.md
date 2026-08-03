# Protocolo do agente

> **Leia isto antes de tocar em qualquer etapa.** Vale para qualquer IA que
> trabalhe no backend do Prisma - Claude, Codex, Gemini, Cursor ou humano.
>
> Este projeto roda num ambiente **multi-agente**: varios agentes trabalham em
> paralelo, no mesmo repositorio, em etapas diferentes. As regras abaixo existem
> para que isso nao vire conflito.

## 1. Uma etapa, um agente, um arquivo

Voce e responsavel por **um** arquivo de `etapas/`. Ele e seu caderno de
trabalho e seu relatorio ao mesmo tempo.

- Nao edite o arquivo de etapa de outro agente. Se precisar de algo de la, leia
  a secao "Contrato de saida" dela e trabalhe contra esse contrato.
- Se descobrir que a etapa de outro agente esta errada, **nao corrija o arquivo
  dele** - registre no seu proprio diario e avise no `README.md` do backend, na
  coluna de observacao da sua linha.

## 2. Escreva enquanto trabalha, nao no fim

**Esta e a regra mais importante deste documento.**

Todo arquivo de etapa tem uma secao **"Diario de execucao"**. Ela nao e um
relatorio final: e um registro **continuo**, escrito durante o trabalho.

Escreva uma entrada quando:

- comecar a etapa (mude o status para `EM ANDAMENTO` e assine);
- tomar uma decisao tecnica que nao estava escrita na etapa;
- encontrar um bug, um bloqueio ou uma contradicao no desenho;
- rodar um teste e observar a saida real;
- terminar um bloco de trabalho, mesmo que a etapa nao esteja concluida.

Formato de cada entrada:

```
- [AAAA-MM-DD] <o que voce fez> - <por que> - <como validou>
```

Por que essa regra existe: se a sua sessao for interrompida (limite de contexto,
falha, troca de modelo), o proximo agente retoma de onde voce parou lendo o seu
diario. Um diario escrito so no fim vira um diario que nunca foi escrito.

**Nunca encerre uma resposta deixando o arquivo marcado como `EM ANDAMENTO` sem
uma entrada nova no diario explicando onde parou.** Se a etapa nao acabou, o
ultimo ato antes de responder e escrever o estado real: o que ficou pronto, o
que falta, qual o proximo passo concreto.

## 3. Status possiveis

Use exatamente estes valores, no cabecalho do arquivo da etapa e na tabela do
[`README.md`](README.md):

| Status | Significa |
|--------|-----------|
| `NAO INICIADA` | Ninguem pegou. Livre. |
| `EM ANDAMENTO` | Alguem esta trabalhando agora. Nao pegue. |
| `BLOQUEADA` | Comecou e travou. O diario diz por que e o que destrava. |
| `AGUARDANDO DECISAO` | Precisa de resposta humana. O diario diz qual e a pergunta. |
| `CONCLUIDA` | Criterio de pronto cumprido e validado com saida real. |

## 4. Antes de comecar, confira as dependencias

Cada etapa declara "Depende de" no cabecalho. Se a etapa de que voce depende
nao esta `CONCLUIDA`, voce tem duas opcoes honestas:

1. escolher outra etapa que esteja livre e sem dependencia pendente; ou
2. comecar a sua **contra o contrato declarado** da etapa anterior, sabendo que
   pode precisar de ajuste - e registrar isso no diario como risco assumido.

Nao implemente a etapa dos outros "de passagem" para se desbloquear.

## 5. Qualidade - o que vale aqui

Este projeto segue o [Felixo System Design](https://github.com/Felipe-Alcantara/Felixo-System-Design).
O contrato minimo, sem precisar abrir os guias:

- **TDD** e o padrao decidido para este backend: teste primeiro, depois
  implementacao. Obrigatorio para regra de negocio, contrato de API e correcao
  de bug.
- **Validacao exige saida real.** "Deve funcionar" nao e validacao. Rode e cole
  a saida observada no diario.
- **Anti-alucinacao**: confirme que uma API, biblioteca ou opcao existe na
  versao instalada antes de usar. Nao presuma de memoria.
- **Um arquivo, uma responsabilidade** ([constituicao](../CONSTITUICAO-MODULARIDADE.md)).
  Modulo Python: 150 linhas ideal, 300 maximo. Sem `utils.py`, `helpers.py`,
  `services.py` gigante.
- **Segredo nunca no repositorio.** Chave de API vive em variavel de ambiente e
  aparece no `.env.example` apenas como nome, sem valor.
- **Entrada externa e sempre validada.** Cobre injecao, XSS, CSRF, authz por
  objeto (nao so por rota) e rate limit onde couber.

## 6. Git

Politica completa em `docs/GIT-POLITICA-DE-VERSIONAMENTO.md` do
[Felixo System Design](https://github.com/Felipe-Alcantara/Felixo-System-Design)
- a copia local fica em `Padrão de qualidade - Felixo System Design/`, que **nao
e versionada** (esta no `.gitignore`). O essencial:

- Commite **direto no `main`**. Nao abra branch por etapa - branch so para
  refatoracao grande ou mudanca de alto risco.
- Commits pequenos, formato `tipo(escopo): descricao no imperativo`. Tipos:
  `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `style`.
- **Commite so os arquivos que voce mexeu.** Outros agentes tem trabalho nao
  commitado no mesmo repositorio: `git add -A` vai levar o trabalho deles junto.
  Use `git add <caminho especifico>`.
- Documentacao entra no **mesmo commit** da mudanca que ela descreve.

## 7. Atualize o `IA.md` da raiz quando a decisao for do projeto

O diario da etapa registra o **trabalho**. O [`IA.md`](../../IA.md) da raiz
registra a **linha do tempo tecnica do projeto**: decisao de arquitetura, bug
relevante, mudanca de rumo.

Regra pratica: se a informacao so interessa a quem for continuar a sua etapa,
fica no diario. Se ela muda como o projeto inteiro funciona, vai tambem para o
`IA.md`, como registro datado - **sem apagar registro antigo**.

## 8. Ferramentas disponiveis

Voce tem CLI de Railway, GitHub e Notion ja autenticadas nesta maquina, e ha
outros repositorios da empresa relacionados a este projeto. Antes de assumir que
algo nao existe ou precisa ser criado do zero, leia
[`FERRAMENTAS-E-ECOSSISTEMA.md`](FERRAMENTAS-E-ECOSSISTEMA.md).
