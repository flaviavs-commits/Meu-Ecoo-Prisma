import { useContext } from 'react'
import { AutenticacaoContexto } from './contexto'

export function useAutenticacao() {
  const contexto = useContext(AutenticacaoContexto)
  if (!contexto) throw new Error('useAutenticacao precisa de AutenticacaoProvider.')
  return contexto
}
