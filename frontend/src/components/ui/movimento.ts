/**
 * Constantes de movimento, compartilhadas por toda a interface.
 *
 * Ficam num lugar só para que ajustar o "tempo" da página seja uma
 * edição, não uma caçada por arquivo. Antes estas curvas estavam
 * copiadas em quatro componentes e já haviam começado a divergir.
 */

/**
 * Curva padrão. Espelha o token `--ease-suave` do CSS - se mudar
 * aqui, mude lá também, para animação em JS e transição em CSS não
 * saírem de sincronia.
 */
export const SUAVE = [0.4, 0, 0.2, 1] as const

/**
 * Curva com leve overshoot: o elemento assenta em vez de frear seco.
 * Use na entrada de títulos e cartões, onde o exagero é bem-vindo.
 */
export const ASSENTA = [0.16, 1, 0.3, 1] as const
