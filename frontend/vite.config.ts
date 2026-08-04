import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Responde numa rota que so este Vite conhece. O HUD usa isso para
// confirmar que quem esta na porta 5173 e o Prisma antes de abrir o
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

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss(), marcadorDev()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => id.includes('node_modules/motion') ? 'motion' : undefined,
      },
    },
  },
})
