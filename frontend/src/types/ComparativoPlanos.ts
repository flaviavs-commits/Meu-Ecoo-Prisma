export interface LinhaComparativoPlano {
  plano: string
  preco: string
  limite: number
  economia: string
}

export interface ComparativoPlanos {
  titulo: string
  linhas: LinhaComparativoPlano[]
  apoio: string
}
