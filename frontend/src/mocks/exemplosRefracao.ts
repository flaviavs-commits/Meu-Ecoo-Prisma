import type { ExemploRefracao } from '../types/ExemploRefracao'

/** Dados locais do protótipo visual do motor de refração. */
export const exemplosRefracao: ExemploRefracao[] = [
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
]
