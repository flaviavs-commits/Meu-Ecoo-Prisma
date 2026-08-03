import { ROTAS } from '../app/routes'

/**
 * Porta de entrada da aplicação.
 *
 * A landing é a vitrine pública. A aplicação em si - as telas de
 * aluno, professor e diretor - vive no repositório `Estudo-com-IA`
 * (pasta `mockup/`) e é trazida para `frontend/public/app/` pelo
 * script `scripts/sincronizar-app.py`. Rode-o de novo sempre que as
 * telas mudarem lá.
 *
 * A aplicação já tem a própria tela inicial ("Como você quer
 * começar?"), que faz a escolha de perfil. Por isso a landing aponta
 * direto para ela, sem perguntar a mesma coisa antes.
 *
 * QUANDO O BACKEND EXISTIR: trocar por uma rota autenticada (o
 * Django servindo a aplicação, ou uma URL de deploy). Só esta
 * constante muda - todos os pontos de "Entrar" leem daqui.
 */

/** Tela inicial da aplicação, destino de todo botão "Entrar". */
export const ENTRADA_APP = ROTAS.app.entrada
