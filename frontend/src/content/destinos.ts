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
 * A entrada autenticada vive no frontend e conversa com a API Django local
 * por meio do cliente em `src/api/cliente.ts`.
 */

/** Raiz onde as telas da aplicação são servidas. */
const BASE_DESTINOS = '/entrar'

/** Tela inicial da aplicação, destino de todo botão "Entrar". */
export const ENTRADA_APP = BASE_DESTINOS
