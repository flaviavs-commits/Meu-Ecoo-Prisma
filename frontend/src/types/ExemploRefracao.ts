import type { PerfilId } from './Perfil'

export interface SaidaRefracao {
  rotulo: string
  perfil: PerfilId
}

export interface ExemploRefracao {
  entrada: string
  saidas: SaidaRefracao[]
}
