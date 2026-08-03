/**
 * Porta de entrada da aplicação.
 *
 * A landing é a vitrine pública. A aplicação definitiva - incluindo
 * login e telas de aluno, professor e diretor - vive em `app/` e é
 * trazida para `frontend/public/app/` pelo script de sincronização.
 *
 * A aplicação já tem a própria tela inicial ("Como você quer
 * começar?"), que faz a escolha de perfil. Por isso a landing aponta
 * direto para ela, sem perguntar a mesma coisa antes.
 *
 * A entrada autenticada vive em `app/login.html` e conversa com a API.
 */

/** Raiz onde as telas da aplicação são servidas. */
const BASE_DESTINOS = '/entrar'

/** Tela inicial da aplicação, destino de todo botão "Entrar". */
export const ENTRADA_APP = BASE_DESTINOS
