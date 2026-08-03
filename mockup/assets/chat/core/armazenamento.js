/* Leitura/escrita de JSON no localStorage, isolada num arquivo so para
   o resto do chat nunca lidar com try/catch de storage diretamente -
   Safari privado e quota cheia lancam excecao em localStorage.setItem,
   e sem isolar isso o app quebraria so por ficar sem espaco. */
const CHAVE = 'prisma-tutor-conversas-v1';

export function carregar() {
  try {
    const bruto = localStorage.getItem(CHAVE);
    return bruto ? JSON.parse(bruto) : null;
  } catch (e) {
    console.warn('[chat] falha ao ler localStorage', e);
    return null;
  }
}

export function salvar(estado) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(estado));
  } catch (e) {
    console.warn('[chat] falha ao gravar localStorage', e);
  }
}
