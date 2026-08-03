# Arquitetura frontend alvo

## Escopo

Este documento define a evolução do frontend do PrismaTest. O escopo desta
fase é exclusivamente a interface React e a migração gradual da aplicação
demonstrativa para componentes React reais. Backend, autenticação, API,
OpenRouter e persistência ficam fora desta etapa.

## Estado atual

- A landing pública está em `frontend/src/`.
- As áreas de aluno, professor e diretor ainda estão em `mockup/`, como HTML,
  CSS e JavaScript estáticos.
- A entrada React renderiza uma única landing, sem roteador, providers,
  contexts, stores, serviços ou dados remotos.
- `mockup/assets/app.js` concentra navegação e interações de três perfis e
  será tratado como legado durante a migração.
- A aplicação demonstrativa não representa autenticação nem autorização reais.

## Arquitetura alvo por camadas

```text
src/
├── app/                 # composição da aplicação, providers e roteamento
├── components/
│   ├── ui/              # componentes visuais reutilizáveis
│   ├── layout/          # shell, header, sidebar e rodapé
│   └── feedback/        # loading, erro, vazio e notificações
├── features/
│   ├── landing/         # seções e composição da landing
│   ├── aluno/           # experiências do aluno
│   ├── professor/       # experiências do professor
│   └── diretor/         # experiências do diretor
├── content/             # copy estática e conteúdo editorial
├── hooks/               # um hook por arquivo, somente quando necessário
├── types/               # contratos pequenos por domínio
├── mocks/               # dados locais temporários, isolados da UI
└── styles/              # tokens e estilos globais quando a divisão for útil
```

As pastas só devem ser criadas quando houver código para justificar a
responsabilidade. Não criar camadas vazias por antecipação.

## Regras de dependência

1. `app` pode compor `features`, `components` e `styles`.
2. `features` pode usar `components`, `content`, `hooks`, `types` e `mocks`.
3. `components/ui` não pode depender de feature, página ou conteúdo de negócio.
4. `content` e `mocks` não renderizam JSX nem acessam o DOM.
5. Componentes não chamam `fetch` diretamente.
6. Dados remotos futuros entrarão por uma camada de acesso definida em tarefa
   própria, sem criar um `api.ts` ou `services.ts` genérico.
7. Providers só serão adicionados quando houver estado transversal real.
8. Cada componente, hook, contexto e tipo novo terá responsabilidade única.

## Composição de aplicação

```text
main.tsx
└── AppProviders
    └── Router
        ├── LandingLayout
        │   └── LandingPage
        └── AppLayout
            ├── StudentRoutes
            ├── TeacherRoutes
            └── DirectorRoutes
```

O roteador e os layouts só entram quando a primeira tela de aplicação for
migrada. A landing não deve ganhar complexidade de autenticação antes de
existir um fluxo real.

## Estados obrigatórios de tela

Toda tela React que consumir dados, mesmo mockados, deverá prever:

- `loading`: carregamento inicial ou operação assíncrona;
- `error`: falha compreensível, com retry quando fizer sentido;
- `empty`: ausência legítima de dados, com orientação de próximo passo;
- `ready`: conteúdo utilizável;
- `pending`: operações iniciadas pelo usuário, sem duplo envio;
- `success`: confirmação de uma ação concluída.

Componentes puramente editoriais podem não precisar desses estados, mas a
decisão deve ser evidente pelo próprio código.

## Mapa de migração

### Passo 1 — arquitetura e contratos

Documentar a estrutura alvo e os limites da migração. Não alterar a UI.

### Passo 2 — fundação de UI

Corrigir contratos de `Button`, `Card` e demais componentes base sem mudar o
visual. Criar tipos discriminados quando um componente puder ser botão ou link.

### Passo 3 — modularidade da UI atual

Separar componentes que hoje compartilham arquivo, especialmente animação,
seção e título, somente onde a responsabilidade realmente divergir.

### Passo 4 — contratos de conteúdo

Criar tipos pequenos para landing, planos, créditos e perfis. Remover lógica
dependente de posição de array ou parsing de strings formatadas.

### Passo 5 — dados mockados isolados

Mover dados de demonstração para `mocks/`, mantendo os componentes livres de
fixtures extensas e preparando a troca futura por dados remotos.

### Passo 6 — primeira tela React de aplicação

Migrar uma tela por vez, começando pela entrada de perfil ou pelo aluno.
Cada migração deve incluir estados de loading, erro e vazio quando aplicável.

### Passo 7 — shell e navegação

Introduzir layouts, roteamento, navegação interna e estados de rota. Só então
adicionar lazy loading, `Suspense` e boundary de erro por área.

### Passo 8 — migração dos perfis

Migrar aluno, professor e diretor em unidades separadas. O HTML legado só deve
ser removido depois de a rota React equivalente ser validada.

### Passo 9 — qualidade frontend

Adicionar testes de componentes e fluxos críticos, testes E2E das rotas,
acessibilidade, responsividade e performance.

## Critério de pronto desta arquitetura

- O escopo frontend está explícito.
- O mockup legado tem uma estratégia de substituição gradual.
- Não foram criadas camadas vazias ou abstrações especulativas.
- A ordem de migração evita misturar refatoração ampla com feature.
- Cada próximo passo pode ser executado e validado como uma unidade pequena.
