/**
 * Conteúdo da landing page do Prisma.
 * Texto separado da apresentação: edite a copy aqui, sem tocar em JSX.
 */

export const marca = {
  nome: 'Prisma',
  descricao:
    'Plataforma de estudos com IA para instituições de ensino: um crédito, três perfis, memória que acompanha o aluno.',
}

export const navegacao = [
  { rotulo: 'Como funciona', href: '#como-funciona' },
  { rotulo: 'Perfis', href: '#perfis' },
  { rotulo: 'Recursos', href: '#recursos' },
  { rotulo: 'Créditos', href: '#creditos' },
  { rotulo: 'Planos', href: '#planos' },
]

export const hero = {
  etiqueta: 'IA aplicada ao ensino',
  titulo: 'Uma entrada. Todo o espectro do ensino.',
  subtitulo:
    'Um tema entra. Saem materiais prontos para aluno, professor e diretor.',
  ctaPrimario: 'Começar agora',
  ctaSecundario: 'Ver como funciona',
  apoio: 'Feito para quem estuda, quem ensina e quem administra o ensino.',
}

/**
 * Exemplos do demo do motor de refração.
 *
 * Cada saída declara para QUEM ela serve. É isso que define a cor
 * exibida — a cor identifica o perfil destinatário, não a posição
 * na lista (ver "REGRA DE COR" em index.css).
 */
export const exemplosRefracao = [
  {
    entrada: 'Fotossíntese — 7º ano',
    saidas: [
      { rotulo: 'Resumo guiado', perfil: 'aluno' },
      { rotulo: 'Quiz de 10 questões', perfil: 'aluno' },
      { rotulo: 'Plano de aula', perfil: 'professor' },
    ],
  },
  {
    entrada: 'Revolução Francesa — Ensino Médio',
    saidas: [
      { rotulo: 'Linha do tempo', perfil: 'aluno' },
      { rotulo: 'Prova dissertativa', perfil: 'professor' },
      { rotulo: 'Relatório da turma', perfil: 'diretor' },
    ],
  },
  {
    entrada: 'Frações — 5º ano',
    saidas: [
      { rotulo: 'Lista progressiva', perfil: 'aluno' },
      { rotulo: 'Exercícios resolvidos', perfil: 'aluno' },
      { rotulo: 'Diagnóstico da turma', perfil: 'professor' },
    ],
  },
  {
    entrada: 'Ciclo da água — 4º ano',
    saidas: [
      { rotulo: 'Mapa visual', perfil: 'aluno' },
      { rotulo: 'Roteiro de aula', perfil: 'professor' },
      { rotulo: 'Indicador de engajamento', perfil: 'diretor' },
    ],
  },
] as const

export const perfis = [
  {
    id: 'aluno',
    nome: 'Aluno',
    foco: 'Estudar com apoio contínuo',
    corVar: 'var(--color-aluno)',
    tintVar: 'var(--color-lavender-tint)',
    itens: [
      'Tutor que lembra o que você já estudou',
      'Simulados com correção comentada',
      'Resumos, flashcards e áudio-revisão gerados na hora',
      'Registro de estudo visível para os responsáveis',
      'Agenda de estudos com sequência e progresso por matéria',
      'Materiais salvos e organizados por matéria',
    ],
  },
  {
    id: 'professor',
    nome: 'Professor',
    foco: 'Ensinar sem o trabalho repetitivo',
    corVar: 'var(--color-professor)',
    tintVar: 'var(--color-terracotta-tint)',
    itens: [
      'Provas geradas a partir do seu conteúdo',
      'Correção assistida por rubrica, sempre com sua revisão',
      'Banco de material reutilizável',
      'Alertas da IA sobre turmas travadas num tópico',
      'Horas de correção devolvidas por mês',
      'Workspaces para organizar turmas e conteúdo',
    ],
  },
  {
    id: 'diretor',
    nome: 'Diretor',
    foco: 'Administrar com visibilidade real',
    corVar: 'var(--color-diretor)',
    tintVar: 'var(--color-olive-tint)',
    itens: [
      'Desempenho por turma em painel',
      'Distribuição de créditos entre perfis',
      'Consumo de IA auditável',
      'Alertas de frequência e turmas abaixo da meta',
      'Relatório mensal com média por série',
      'Gestão de equipe e permissões de acesso',
    ],
  },
]

export const recursos = [
  {
    titulo: 'Motor multi-modelo',
    descricao: 'Cada tarefa vai para o modelo mais adequado em custo.',
  },
  {
    titulo: 'Memória persistente',
    descricao: 'O tutor retoma o contexto do aluno sem reler tudo.',
  },
  {
    titulo: 'Créditos auditáveis',
    descricao: 'Consumo de IA visível por perfil.',
  },
  {
    titulo: 'Revisão do professor',
    descricao: 'Conteúdo de IA nasce rascunho. Quem ensina aprova.',
  },
  {
    titulo: 'Dados criptografados',
    descricao: 'Conversas e histórico do aluno são criptografados de ponta a ponta, isolados por instituição.',
  },
  {
    titulo: 'Painel por turma',
    descricao: 'Progresso, engajamento e uso de IA visíveis por turma, em tempo real.',
  },
]

/**
 * Planos de tokens do aluno individual - independente do plano
 * institucional (ver `creditos`). O aluno começa no mínimo e pode
 * subir de plano quando quiser, sem depender da escola.
 *
 * Preço e volume de tokens ainda não definidos: "x" é placeholder,
 * não publique com valor real até a precificação fechar.
 */
export const planos = {
  etiqueta: 'Planos',
  titulo: 'Comece no mínimo. Suba quando quiser.',
  descricao:
    'Três planos de tokens para quem estuda por conta própria. Sem contrato, sem fidelidade.',
  /** Comum aos três planos - não repetir dentro de cada card. */
  baseComum: 'Todo plano inclui tutor com memória, simulados com correção e histórico de estudo.',
  itens: [
    {
      id: 'prisma',
      nome: 'Prisma',
      resumo: 'Para testar o tutor e organizar os estudos',
      preco: 'R$ 39,99',
      periodo: '/mês',
      destaque: false,
      itens: [
        '100% do limite padrão de uso',
        'Resumos, flashcards e áudio-revisão gerados na hora',
        'Agenda de estudos com sequência e progresso por matéria',
      ],
    },
    {
      id: 'prisma-pro',
      nome: 'Prisma Pro',
      resumo: 'Para quem estuda todo dia e não quer esperar',
      preco: 'R$ 64,99',
      periodo: '/mês',
      destaque: true,
      itens: [
        '71% a mais de limite de uso que o Prisma',
        'Respostas do tutor com prioridade',
        'Plano de estudo semanal gerado pela IA',
      ],
    },
    {
      id: 'prisma-ultra',
      nome: 'Prisma Ultra',
      resumo: 'Para quem quer o tutor no limite',
      preco: 'R$ 99,99',
      periodo: '/mês',
      destaque: false,
      itens: [
        '171% a mais de limite de uso que o Prisma',
        'Acesso aos modelos de IA mais avançados do motor',
        'Suporte prioritário',
      ],
    },
  ],
} as const

export const creditos = {
  etiqueta: 'Créditos',
  titulo: 'A instituição assina. O diretor distribui.',
  descricao:
    'Um saldo por assinatura. A escola decide quanto cada perfil usa.',
  pontos: [
    'Distribuição ajustável por perfil e turma',
    'Consumo monitorado em tempo real',
    'Alerta quando um perfil está perto do limite',
  ],
  /**
   * Comparação de valor entre os 3 planos individuais (ver `planos`).
   * "economia" é o custo por unidade de limite de uso, medido contra
   * o Prisma - por isso o Prisma aparece com 0%. Números derivados do
   * preço e do limite de cada plano; não são estimativa de marketing.
   */
  comparativoPlanos: {
    titulo: 'Quanto mais o plano, mais barato o limite de uso',
    linhas: [
      { plano: 'Prisma', preco: 'R$ 39,99', limite: '100%', economia: 'referência' },
      { plano: 'Prisma Pro', preco: 'R$ 64,99', limite: '171%', economia: '5%' },
      { plano: 'Prisma Ultra', preco: 'R$ 99,99', limite: '271%', economia: '7,7%' },
    ],
    apoio: 'Economia por unidade de limite de uso, comparada ao Prisma.',
  },
}

export const ctaFinal = {
  titulo: 'Pronto para começar?',
  descricao: 'Configure a escola e distribua os primeiros créditos.',
  botao: 'Criar conta da instituição',
  apoio: 'Migração de dados com apoio da equipe.',
}

/** Contatos do rodapé. Paths de ícone em 24x24. */
export const contatos = [
  {
    rotulo: 'E-mail',
    href: '#',
    icone: 'M3 7l9 6 9-6M4 5h16a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V6a1 1 0 011-1z',
  },
  {
    rotulo: 'Para escolas',
    href: '#',
    icone: 'M3 8h18v11a1 1 0 01-1 1H4a1 1 0 01-1-1V8zM9 8V5a1 1 0 011-1h4a1 1 0 011 1v3',
  },
  {
    rotulo: 'Demonstração',
    href: '#',
    icone: 'M4 4h16a1 1 0 011 1v14a1 1 0 01-1 1H4a1 1 0 01-1-1V5a1 1 0 011-1zM10 9l5 3-5 3V9z',
  },
]

export const rodape = {
  colunas: [
    {
      titulo: 'Produto',
      links: [
        { rotulo: 'Como funciona', href: '#como-funciona' },
        { rotulo: 'Perfis', href: '#perfis' },
        { rotulo: 'Recursos', href: '#recursos' },
        { rotulo: 'Créditos', href: '#creditos' },
        { rotulo: 'Planos', href: '#planos' },
      ],
    },
    {
      titulo: 'Instituição',
      links: [
        { rotulo: 'Sobre', href: '#' },
        { rotulo: 'Contato', href: '#' },
        { rotulo: 'Suporte', href: '#' },
      ],
    },
    {
      titulo: 'Legal',
      links: [
        { rotulo: 'Privacidade', href: '#' },
        { rotulo: 'Termos de uso', href: '#' },
        { rotulo: 'Segurança', href: '#' },
      ],
    },
  ],
}
