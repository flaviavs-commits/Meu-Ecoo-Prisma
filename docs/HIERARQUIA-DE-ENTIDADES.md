# Hierarquia das entidades do Sistema Prisma

> **Fonte de verdade:** o canvas "Sistema Prisma"
> (`Untitled-2026-06-19-1523.png`). Este documento é o espelho dele no
> repositório, com o estado do código anotado em cada ponto.
>
> **Como usar:** para saber *o que o produto é*, leia as seções 2 a 6. Para
> saber *onde isso mora no código*, leia a coluna "Implementação" de cada tier.

## 1. Os cinco tiers

Do mais amplo para o mais restrito:

| # | Tier | Instituição | Perfil (`contas.Perfil`) | Alcance |
|---|------|-------------|--------------------------|---------|
| 1 | SuperAdmin | Vitis Souls (`PROVEDORA`) | `PROVIDER` | Irrestrito, cross-tenant |
| 2 | Administrador | Prisma (`PRISMA`) | `ADMINISTRADOR` | Cross-tenant, só usuário e monitoramento |
| 3 | Diretor | Escola (`ESCOLA`) | `DIRETOR` | A própria instituição |
| 4 | Professor | Escola (`ESCOLA`) | `PROFESSOR` | Os próprios alunos |
| 5 | Aluno | Escola (`ESCOLA`) | `ALUNO` | O próprio conteúdo e o próprio limite |

Os tiers 1 e 2 são **a equipe** (`contas.PERFIS_INTERNOS`) e moram em
instituições internas (`contas.TIPOS_INTERNOS`). Os tiers 3 a 5 são **contas
de instituição-cliente** e vivem sob o isolamento por `instituicao_id`.

Cada instituição interna aceita exatamente um perfil — o mapa é
`contas.PERFIL_POR_TIPO_INTERNO`, e `Usuario.clean()` é quem cobra a regra.
Instituição interna não hospeda conta acadêmica e não contrata plano
comercial.

## 2. SuperAdmin — instituição "Vitis Souls"

**Definição.** Perfil `PROVIDER`, vinculado à instituição interna da Vitis
Souls (tipo `PROVEDORA`, código reservado `VITIS_SOULS`). Representa a equipe
própria do produto, não uma instituição contratante.

> O canvas chama este tier de "Mantenedor ou provider". O nome oficial passou
> a ser **provider** em 2026-08-06; `MANTENEDOR`/`MANTENEDORA` era o nome
> anterior dos mesmos registros.

**Permissões.** Acesso irrestrito a todas as entidades, independentemente da
instituição — o SuperAdmin não está sujeito ao isolamento por `instituicao_id`.
Pode criar, editar e desativar contas de qualquer perfil e instituição
(incluindo contas de teste); criar, alterar e arquivar qualquer entidade do
domínio (instituições, turmas, matrículas, conteúdo, créditos, planos); e
operar pelo painel administrativo dedicado (`painel_admin`), separado da API
consumida pelo frontend das escolas.

**Finalidade.** Uso interno, restrito ao time técnico e à liderança: suporte,
auditoria, testes de regressão entre tiers e operações financeiras.

**Implementação.**
- `contas.Perfil.PROVIDER` e `Usuario.eh_provider`;
- `painel_admin.permissoes.exige_superadmin` barra quem não for provider;
- não há permission class de escopo aplicada a ele — **a ausência de filtro por
  instituição é o que garante o acesso cross-tenant**.

## 3. Administrador — instituição "Prisma"

**Definição.** Perfil `ADMINISTRADOR`, vinculado à instituição interna Prisma
(tipo `PRISMA`, código reservado `PRISMA`). Camada de staff da operação, com
escopo administrativo sobre as instituições-cliente — distinta do SuperAdmin
**em profundidade, não em alcance**: opera sobre usuário e monitoramento, não
sobre a totalidade das entidades.

**Permissões.**
- gestão de usuários das instituições-cliente: consulta, edição e desativação
  de contas (Aluno, Professor, Diretor);
- monitoramento das instituições: status, uso e saúde operacional;
- leitura de indicadores agregados, **sem** permissão de escrita sobre
  entidades de domínio (turmas, conteúdo, créditos, planos).

**Finalidade.** Funcionários que sustentam a operação do produto — suporte,
sucesso do cliente, administração — sem a necessidade (nem o risco) de deter
permissões absolutas.

**Implementação.**
- `contas.Perfil.ADMINISTRADOR`, `Usuario.eh_administrador` e
  `Usuario.eh_staff_interno` (provider *ou* administrador);
- `contas.permissoes.EAdministrador`, nos moldes de `EDiretor`/`EProfessor`;
- `painel_admin.permissoes.exige_staff_interno` abre as views de usuário e
  monitoramento (`dashboard`, `instituicoes`, `instituicao`, `usuarios`,
  `usuario`, `usuario_editar`, `usuario_desativar`). As demais continuam em
  `exige_superadmin`: criação/edição/arquivamento de instituição, contas de
  teste, troca de perfil, zerar créditos e auditoria;
- três guardas em `painel_admin.services.editar_usuario` impedem que o
  administrador edite conta da equipe, conceda perfil da equipe ou mova conta
  para uma instituição interna — sem elas, ele se promoveria a SuperAdmin.

**Nunca** carrega `is_superuser`: `Usuario.clean()` recusa a combinação.

## 4. Diretor — instituição escolar

**Definição.** Perfil `DIRETOR`, vinculado a uma instituição-cliente do tipo
`ESCOLA`. Responsabilidade estritamente contida ao escopo da própria
instituição — sem visibilidade nem ação sobre qualquer outra escola.

**Permissões.** Gestão das contas filhas da sua instituição; monitoramento
acadêmico (notas lançadas, relatórios de desempenho); controle de limites de
uso de todas as contas do seu escopo; e visibilidade sobre o **conteúdo oficial
dos professores** — o que já passou pela oficialização (`Prova.status =
OFICIAL`, `Nota.oficial = True`). Conteúdo gerado por alunos (ex.: simulados
individuais) fica **fora** desse escopo: é uso pessoal, não produção
institucional.

**Modelo comercial.** Os planos são assinados exclusivamente pela instituição,
nunca por conta individual. A assinatura tem periodicidade **mensal ou anual**
(`limites.Periodicidade`), e a instituição monitora o uso agregado das contas
no seu escopo.

> A periodicidade da cobrança (`AssinaturaInstituicao.periodicidade`) não se
> confunde com o ciclo de apuração de consumo (`limites/ciclo.py`), que é
> sempre mensal. Uma assinatura anual tem doze janelas mensais de uso.

**Estrutura de turmas.** O diretor monitora múltiplas turmas. **Cada turma tem
N professores e cada professor leciona em N turmas** — relação
muitos-para-muitos em `academico.Turma.professores`. O campo
`professor_responsavel` permanece como **titular** da turma (quem responde por
ela), e o titular é sempre um dos professores. `Turma.leciona(usuario)` é a
pergunta única de "esta pessoa dá aula aqui?".

## 5. Professor — instituição escolar

**Definição.** Perfil `PROFESSOR`. Escopo restrito às contas de aluno sob sua
supervisão — mais estreito que o do diretor, que enxerga a instituição toda.

**Permissões.**
- gestão limitada aos próprios alunos, sem visibilidade sobre outros
  professores, turmas ou diretores;
- visibilidade de cota restrita ao próprio uso;
- monitoramento acadêmico dos próprios alunos, gerando o insumo que alimenta o
  monitoramento mais amplo do diretor;
- **distribuição de conteúdo**: envia avisos, materiais, simulados, trabalhos e
  planos de aula, **com data e prazo de entrega** das atividades propostas;
- geração assistida por IA, que **nasce como rascunho** — conteúdo de IA só
  vira oficial por ação explícita do professor;
- análise de desempenho dos próprios alunos; simulados gerados pelo aluno ficam
  fora desse escopo, mesma fronteira do diretor.

**Implementação dos dois pontos que faltavam.**
- **Avisos:** app `avisos` (`Aviso`, `avisos.servico.enviar_aviso`,
  `GET`/`POST /api/v1/avisos/`). O destinatário é a **turma**, não o aluno:
  quem lê é quem está matriculado nela no momento da leitura, então matrícula
  nova já enxerga o histórico e matrícula encerrada para de enxergar. Envia
  quem leciona na turma; o diretor envia para qualquer turma da escola.
- **Prazo de entrega:** `conteudo.Material.prazo_entrega` e
  `conteudo.Prova.prazo_entrega` (nulo quando não há atividade a entregar).
  `Aviso.prazo_entrega` acompanha, pelo mesmo motivo.

## 6. Aluno — instituição escolar

**Definição.** Perfil `ALUNO`, o nível mais básico. Escopo restrito ao que é
seu: os próprios conteúdos e o próprio limite de uso — sem visibilidade sobre
outros alunos, professores ou dados agregados da instituição.

**Permissões.** Upload e organização de conteúdo; geração de material via IA
nos quatro formatos do catálogo inicial (**resumo**, **flashcards**,
**áudio-revisão**, **simulado** com correção automática); tutor de IA com
memória consolidada entre sessões; agenda de estudos (pendente, concluído,
cancelado); e análise assistida por IA do próprio material, com download
livre dos próprios arquivos.

**Limite de uso.** O consumo de IA é contabilizado pela plataforma em ciclo
mensal (`limites/ciclo.py`). Duas regras sustentam o desenho:

**1. O limite é do plano, nunca da pessoa.** Todas as contas de uma escola —
aluno, professor e diretor — têm exatamente a mesma capacidade, a do plano que
a instituição contratou. **Não existe cota nominal**: ninguém aumenta nem
reduz o limite de uma conta isolada, nem a equipe interna, nem o diretor.
Muda-se o plano da escola (`limites.atualizar_plano`), e muda para todos.

**2. A conta sempre lê 100%.** Internamente cada plano tem uma capacidade
diferente — Prisma `100`, Pro `171`, Ultra `271` (número comercial, público na
landing). Mas a conta enxerga sempre a régua de **0 a 100%**: todo mundo vê
"100%", e o que aquele 100% comporta de uso real é que difere entre os planos.
A conversão fica em `limites/normalizacao.py`, deliberadamente separada do
serviço — normalizar é operação de **leitura**, nunca de autorização; o portão
(`autorizar_uso`) continua decidindo sobre o estado interno.

Isso dá duas propriedades que o produto quer:

- a conta não descobre o custo nem o tamanho do plano. O histórico próprio
  (`/api/v1/limites/uso/historico/`) expõe só `classe_tarefa`, `ciclo` e o
  percentual reescalado — `fornecedor`, `modelo` e `custo_bruto` ficam no
  modelo como telemetria server-side, porque a plataforma opera **vários
  provedores** e a conversão custo→percentual é ajustada conforme a demanda
  geral do aplicativo. Expor o provedor exporia uma mecânica que muda debaixo
  do usuário e não significa nada para ele;
- trocar de plano não muda a escala que a conta lê. Quem estava em 40% no
  Prisma continua em 40% depois do upgrade — o que cresceu foi o que cabe
  dentro daqueles 40%, não o número na tela.

> **É isto que "ajustado conforme a demanda" significa** no canvas: a
> plataforma ajusta a conversão custo→percentual no lado dela, conforme o uso
> geral e o mix de provedores. **Não** é um botão para dar mais cota a um aluno
> específico.

**Ainda não construído.** A API que monitora o custo real por conta — cada
conta com a sua Key, acompanhada por um módulo de IA, somando o gasto entre
provedores de modelos de cobrança diferentes — **não existe**. Hoje o que
existe é `ia/conversao.py`, uma conversão global custo-em-dólar → percentual
(`IA_CUSTO_DOLAR_POR_PERCENTUAL` × margem), que só funciona para provedor
cobrado por token. Ver a seção 8.

**Escopo do produto.** O conjunto é deliberadamente enxuto — está em beta, e a
expectativa declarada é de expansão. Os quatro formatos são o catálogo
inicial, não o teto.

## 7. Auditoria de 2026-08-06: o que o canvas apontava e o que foi feito

O canvas trazia seis divergências marcadas com ⚠️. Todas foram confirmadas no
código e corrigidas — a imagem é a fonte de verdade, então o código andou até
ela.

| # | O canvas dizia | O código tinha | O que passou a existir |
|---|----------------|----------------|------------------------|
| 1 | Tier "Administradores — instituição Prisma" | Só `MANTENEDOR`; nenhuma camada intermediária | `Perfil.ADMINISTRADOR`, `EAdministrador`, `exige_staff_interno`, instituição interna `PRISMA` |
| 2 | "Cada turma pode ter N professores" | `professor_responsavel` FK simples | `Turma.professores` (M2M) + `Turma.leciona()`, com backfill do titular |
| 3 | "Assinatura mensal ou anual" | `AssinaturaInstituicao` sem periodicidade | `Periodicidade` (MENSAL/ANUAL) e `total_por_cobranca` |
| 4 | Professor "envia avisos aos alunos" | Nenhum model de aviso | App `avisos` com escopo por turma |
| 5 | Conteúdo "com data e prazo de entrega" | Material/Prova só com status e datas de criação | `prazo_entrega` em `Material`, `Prova` e `Aviso` |
| 6 | Limite do aluno "ajustado conforme a demanda" | Conta lia o número bruto do plano (100/171/271) e via fornecedor e modelo no próprio histórico | `limites/normalizacao.py`: a conta lê sempre 0–100%, e o histórico dela perde `fornecedor`/`modelo` |

> **Correção de rumo no item 6.** Numa primeira leitura eu entendi "ajustado
> conforme a demanda" como ajuste nominal de cota por aluno e cheguei a
> implementar um `AjusteCotaUsuario`. A usuária corrigiu: o limite **não** é
> ligado ao aluno e não sobe nem desce por conta. O que se ajusta conforme a
> demanda é a conversão custo→percentual, do lado da plataforma. O modelo, o
> serviço, a rota e os testes daquele ajuste foram removidos, e no lugar entrou
> a normalização descrita na seção 6.

No mesmo passo, o tier `MANTENEDOR` foi renomeado para `PROVIDER` (e
`MANTENEDORA` para `PROVEDORA`), por decisão da usuária registrada no canvas
("SuperAdmins — Vitis Souls (Mantenedor ou provider)").

**Migrações de dados envolvidas** — todas rodam no predeploy do Railway:

- `contas.0008_provider_e_instituicao_prisma` — renomeia os valores gravados,
  promove a instituição "Prisma" (que existia como `ESCOLA` com documento
  `Dono`) ao tipo interno `PRISMA`, e move as contas acadêmicas que moravam
  nela para uma "Escola de Testes Prisma", porque instituição interna não
  hospeda aluno, professor nem diretor;
- `academico.0004_turma_professores` — matricula o titular atual como
  professor da turma, para que nenhuma turma perca o professor que já tinha;
- `limites.0004_periodicidade_assinatura`, `conteudo.0004_prazo_de_entrega`,
  `avisos.0001_initial`, `custos.0001_initial`, `custos.0003_assinatura_relativa`
  — só schema;
- `custos.0002_catalogo_inicial` e `custos.0004_catalogo_relativo` — semeiam os
  três contratos de fornecedor e os fatores sobre a referência (ver seção 8).
  Sem eles, chamada por assinatura chega com custo zero e não consome nada.

## 8. Medir custo entre provedores de cobrança diferente

A régua de 0 a 100% da seção 6 depende de uma pergunta: quanto custou, de
verdade, uma chamada? A resposta não pode ser a mesma fórmula para todo mundo,
porque os fornecedores não cobram do mesmo jeito:

| Fornecedor | Cobrança | Custo marginal de uma chamada |
|------------|----------|-------------------------------|
| OpenRouter (Deepseek V4 Flash) | por token | real, conhecido na hora |
| Claude (Sonnet) | assinatura mensal | zero na margem; o custo é uma fatia da mensalidade |
| GPT / Codex (Luna) | assinatura mensal | idem |

Antes, `ia/conversao.py` recebia direto o `custo_bruto` que o provedor
reportava. Numa assinatura esse valor é **zero** — a chamada não consumia nada
da conta, e o medidor parava de medir justamente onde a capacidade é escassa.

**O app `custos` responde essa pergunta.** Cada fornecedor tem um
`ContratoProvedor` que declara como o custo dele é apurado, e
`custos/rateio.py` devolve o custo da chamada em dólar para qualquer um deles:

| Modalidade | Como mede | Quando usar |
|------------|-----------|-------------|
| `POR_TOKEN` | custo real reportado; na falta, a `TarifaModelo` do catálogo | fornecedor cobrado por uso |
| `ASSINATURA_RELATIVA` | `fator × o que a chamada custaria na referência` | **recomendada** para assinatura |
| `ASSINATURA_RATEIO` | `mensalidade ÷ (contas × chamadas por conta)` | assinatura cuja capacidade se conhece bem |

A modalidade relativa é a que sustenta a intuição de negócio: **um fator de
0,4 diz "esta chamada pesa 40% do que pesaria no OpenRouter"**. Uma conta
Claude Max bem diluída recebe um fator pequeno e passa a alimentar centenas de
alunos sem comprometer o limite de ninguém — e basta um número para ajustar
isso, em vez de duas estimativas difíceis de acertar.

Ancorar no fornecedor por token, em vez de num valor absoluto, dá duas
propriedades de graça: o peso da assinatura **acompanha sozinho o tamanho da
chamada** (uma conversa longa pesa mais que uma curta) e **sobrevive a mudança
de preço de mercado** (se a referência encarece, a assinatura encarece na mesma
proporção, sem ninguém reescrever número nenhum). A tarifa que serve de régua é
a marcada com `TarifaModelo.referencia`.

Com os fatores iniciais, a mesma chamada de 1k de entrada e 0,5k de saída vale:

| Fornecedor | Peso | Custo |
|------------|------|-------|
| OpenRouter / Deepseek V4 Flash | 1x (referência) | US$ 0,00045000 |
| Claude Sonnet (assinatura) | 0,40x | US$ 0,00018000 |
| GPT Luna (assinatura) | 0,50x | US$ 0,00022500 |

Ou seja: **o OpenRouter consome mais rápido e a assinatura consome devagar**,
que é o comportamento esperado. O gateway chama `custo_da_chamada()` antes de
converter em percentual — é isso que torna a contagem indiferente ao
fornecedor: trocar de provedor no meio do mês não interrompe a medição nem
muda a escala que a conta lê, muda só a velocidade com que ela consome.

### "O monitoramento deve acompanhar a mudança"

Nos dois modos existe um número que envelhece se ninguém o corrigir:

- na **relativa**, é o `fator_sobre_referencia`. Migrar as contas para um plano
  maior do mesmo fornecedor barateia a chamada — o fator desce, e a mesma
  conversa passa a consumir menos do limite de todo mundo;
- no **rateio**, são `contas_atendidas` e `chamadas_por_conta_no_mes`. Se uma
  assinatura que atendia 200 contas passa a atender 400, a mesma mensalidade se
  dilui no dobro do uso e o custo por chamada cai pela metade.
  `custos/recalibracao.py` faz esse ajuste, auditado e restrito à equipe interna
  — contrato com fornecedor é da plataforma, não da escola.

### A garantia que sustenta tudo

**Recalibrar vale só para as chamadas seguintes.** O percentual é calculado no
momento do débito e gravado em `ConsumoIA`, que é append-only e nunca
recalculado. A camada do provedor pode se mover à vontade — remanejar
assinaturas, trocar fornecedor, reestimar capacidade — e nada disso mexe no
que a conta já viu consumido. **A camada de provedor não é fonte de verdade da
porcentagem do usuário**; ela só influencia o preço das chamadas futuras. Por
isso o percentual da conta só anda numa direção dentro da competência: para
baixo, conforme o uso.

Coberto por `custos/tests/test_recalibracao.py::
test_recalibrar_nao_mexe_no_consumo_ja_debitado`.

> **Os fatores e preços do catálogo inicial são ponto de partida operacional,
> não verdade contábil** (ver `custos/migrations/0002_catalogo_inicial.py` e
> `0004_catalogo_relativo.py`). Calibrá-los contra o uso real é o primeiro
> trabalho do painel — a tela `/painel/uso/` mostra chamadas e custo por
> fornecedor justamente para isso.

## 9. O painel administrativo por hierarquia

O painel Django (`/painel/`) é **o mesmo site para todos os tiers**; o que muda
é o recorte da conta logada. O portão externo é
`painel_admin.permissoes.exige_acesso_ao_painel` (provider, administrador ou
diretor de escola), e o recorte vive em `painel_admin/escopo.py` — um lugar
só, para que o isolamento entre escolas possa ser lido e testado de uma vez.

| | Provider | Administrador | Diretor |
|---|:---:|:---:|:---:|
| Visão geral, usuários, uso de IA | tudo | tudo | **só a própria escola** |
| Custo em dólar e contratos de fornecedor | vê | vê | **não vê** |
| Desativar conta | sim | sim | só da própria escola |
| Editar conta, instituições, contas de teste | sim | edita conta | não |
| Trocar perfil, zerar créditos, auditoria | sim | não | não |

Duas decisões que valem registro:

- **o diretor não vê custo em dólar.** O contrato de produto com a escola é
  percentual; quanto a plataforma paga a cada fornecedor é assunto dela. Ele
  monitora as contas da escola na mesma régua que elas enxergam;
- **conta fora do escopo responde 404, não 403.** Um 403 confirmaria que a
  conta existe. As views com `@painel_required` fazem `get_object_or_404`
  sobre a queryset do escopo, nunca sobre o modelo direto — inclusive a de
  desativar, que antes distinguia os dois casos pelo status.

