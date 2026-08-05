import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Responde numa rota que so este Vite conhece. O HUD usa isso para
// confirmar que quem esta na porta escolhida e o Prisma antes de abrir o
// navegador - sem isso, outro Vite (de outro projeto) escutando na
// mesma porta seria aberto como se fosse a landing page do Prisma.
function marcadorDev(): Plugin {
  return {
    name: 'prisma-dev-marker',
    configureServer(servidor) {
      servidor.middlewares.use('/__prisma_dev_marker', (_req, res) => {
        res.statusCode = 200
        res.setHeader('Content-Type', 'text/plain')
        res.end('prisma')
      })
    },
  }
}

/**
 * Injeta <link rel="preload"> para as fontes que a pagina realmente
 * pinta no primeiro quadro.
 *
 * Sem preload, o navegador so descobre a fonte depois de baixar E
 * interpretar o CSS - a fonte fica no terceiro nivel da cascata de
 * dependencias. Com preload no HTML, o download comeca junto com o do
 * CSS.
 *
 * So as variantes `latin` entram: `latin-ext` tem unicode-range que o
 * portugues nao aciona, e um preload nao usado desperdicaria banda no
 * caminho critico (o Chrome ainda avisa no console).
 *
 * Le os nomes do proprio bundle porque o Vite poe hash de conteudo no
 * arquivo - fixar o nome a mao quebraria a cada rebuild.
 */
function preloadDeFontes(): Plugin {
  return {
    name: 'prisma-preload-fontes',
    enforce: 'post',
    transformIndexHtml(_html, ctx) {
      const fontes = Object.keys(ctx.bundle ?? {}).filter(
        (arquivo) => arquivo.endsWith('.woff2') && arquivo.includes('latin-'),
      )
      // `latin-ext` tambem casa com "latin-", entao filtramos de novo.
      const criticas = fontes.filter((f) => !f.includes('latin-ext'))

      return criticas.map((arquivo) => ({
        tag: 'link',
        attrs: {
          rel: 'preload',
          as: 'font',
          type: 'font/woff2',
          href: `/${arquivo}`,
          crossorigin: '',
        },
        injectTo: 'head-prepend' as const,
      }))
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), marcadorDev(), preloadDeFontes()],
  server: {
    // Mantem o comando direto alinhado ao HUD. Com `strictPort` desligado,
    // o Vite tenta a proxima porta livre a partir desta quando necessario.
    port: 5176,
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => id.includes('node_modules/motion') ? 'motion' : undefined,
      },
    },
  },
})
