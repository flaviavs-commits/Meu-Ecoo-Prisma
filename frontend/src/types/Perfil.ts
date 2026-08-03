export type PerfilId = 'aluno' | 'professor' | 'diretor'

export interface Perfil {
  id: PerfilId
  nome: string
  foco: string
  corVar: string
  tintVar: string
  itens: string[]
}
