import { cp, mkdir, rm } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const origem = resolve(frontend, '..', 'app')
const destino = resolve(frontend, 'public', 'app')

await mkdir(resolve(frontend, 'public'), { recursive: true })
await rm(destino, { recursive: true, force: true })
await cp(origem, destino, { recursive: true })

console.log(`Aplicacao sincronizada para ${destino}`)
