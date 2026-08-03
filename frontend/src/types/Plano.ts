export type PlanoDestaque = 'recomendado' | 'premium' | null

export interface Plano {
  id: string
  nome: string
  resumo: string
  preco: string
  periodo: string
  destaque: PlanoDestaque
  itens: string[]
}
