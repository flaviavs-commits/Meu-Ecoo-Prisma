import { motion } from 'motion/react'
import { Secao } from '../ui/Secao'
import { ItemAnimado, ListaAnimada } from '../ui/Animar'
import { Titulo3D } from '../ui/Titulo3D'
import { creditos } from '../../content/landing'
import { SUAVE } from '../ui/movimento'

/**
 * Cor de destaque por plano - mesmas do espectro de perfil, usadas
 * aqui só como identidade visual do card, sem relação com perfil.
 */
const corPorPlano: Record<string, string> = {
  Prisma: 'var(--color-aluno)',
  'Prisma Pro': 'var(--color-professor)',
  'Prisma Ultra': 'var(--color-diretor)',
}

/**
 * Teto da barra comparativa: o maior "limite" entre os planos, derivado
 * dos dados em vez de fixo. Um valor fixo (ex. 271) quebraria em silêncio
 * se um plano mudasse de limite ou um novo plano fosse adicionado sem
 * que alguém lembrasse de atualizar esse número em dois lugares.
 */
const limiteMaximo = Math.max(
  ...creditos.comparativoPlanos.linhas.map((linha) => parseFloat(linha.limite)),
)

/** Explica o modelo de créditos e a distribuição pelo diretor. */
export function Creditos() {
  return (
    <Secao id="creditos" fundo="diretor">
      <div className="grid items-center gap-12 lg:grid-cols-2">
        <div>
          {/* Mesma régua de capítulo das demais seções */}
          <div className="flex items-center gap-4 text-texto-secundario">
            <span className="h-px w-12 bg-contorno-forte" />
            <span className="text-xs tracking-[0.16em] uppercase">
              {creditos.etiqueta}
            </span>
          </div>

          <h2 className="fonte-display mt-8 text-4xl leading-[1.05] text-balance sm:text-5xl">
            <Titulo3D texto={creditos.titulo} clima="diretor" />
          </h2>
          <p className="mt-6 max-w-md text-lg leading-relaxed text-texto-secundario text-pretty">
            {creditos.descricao}
          </p>

          <ul className="mt-8 space-y-4">
            {creditos.pontos.map((ponto) => (
              <li key={ponto} className="flex gap-3">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 20 20"
                  fill="none"
                  aria-hidden="true"
                  className="mt-0.5 shrink-0 text-texto"
                >
                  <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="1.5" opacity="0.3" />
                  <path
                    d="M6 10.5l2.5 2.5L14 7.5"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <span className="text-texto-secundario">{ponto}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Comparativo animado de valor entre os planos individuais */}
        <div className="rounded-lg border border-contorno bg-superficie p-7 sm:p-8">
          <h3 className="fonte-display text-lg">{creditos.comparativoPlanos.titulo}</h3>

          {/*
            Uma barra só, repartida por plano - a largura de cada
            trecho é proporcional ao limite de uso, então a barra
            inteira já comunica a progressão antes mesmo da tabela.
          */}
          <motion.div
            aria-hidden="true"
            className="mt-6 flex h-2.5 overflow-hidden rounded-full bg-superficie-alt"
            initial="oculto"
            whileInView="visivel"
            viewport={{ once: true, margin: '-80px' }}
            variants={{ visivel: { transition: { staggerChildren: 0.12 } } }}
          >
            {creditos.comparativoPlanos.linhas.map((linha) => (
              <motion.span
                key={linha.plano}
                style={{ backgroundColor: corPorPlano[linha.plano] }}
                variants={{
                  oculto: { width: 0 },
                  visivel: { width: `${(parseFloat(linha.limite) / limiteMaximo) * 100}%` },
                }}
                transition={{ duration: 0.7, ease: SUAVE }}
              />
            ))}
          </motion.div>

          <ListaAnimada className="mt-6" intervalo={0.1}>
            <ItemAnimado>
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="border-b border-borda text-left text-xs tracking-widest text-texto-secundario uppercase">
                    <th className="pb-3 font-medium">Plano</th>
                    <th className="pb-3 font-medium">Preço</th>
                    <th className="pb-3 font-medium">Limite de uso</th>
                    <th className="pb-3 font-medium">Economia</th>
                  </tr>
                </thead>
                <tbody>
                  {creditos.comparativoPlanos.linhas.map((linha) => (
                    <tr key={linha.plano} className="border-b border-borda last:border-0">
                      <td className="py-3.5 font-medium">
                        <span className="flex items-center gap-2.5">
                          <span
                            aria-hidden="true"
                            className="h-2.5 w-2.5 rounded-full"
                            style={{ backgroundColor: corPorPlano[linha.plano] }}
                          />
                          {linha.plano}
                        </span>
                      </td>
                      <td className="py-3.5 tabular-nums text-texto-secundario">{linha.preco}</td>
                      <td className="py-3.5 tabular-nums text-texto-secundario">{linha.limite}</td>
                      <td className="py-3.5 tabular-nums">
                        {linha.economia === 'referência' ? (
                          <span className="text-xs tracking-wide text-texto-secundario uppercase">
                            {linha.economia}
                          </span>
                        ) : (
                          <span className="fonte-display text-xs font-bold text-sucesso">
                            ↓ {linha.economia}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </ItemAnimado>
          </ListaAnimada>

          <p className="mt-6 border-t border-borda pt-4 text-xs text-texto-secundario">
            {creditos.comparativoPlanos.apoio}
          </p>
        </div>
      </div>
    </Secao>
  )
}
