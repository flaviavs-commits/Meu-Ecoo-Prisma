import { Header } from './components/layout/Header'
import { Rodape } from './components/layout/Rodape'
import { Hero } from './components/feature/Hero'
import { MotorRefracao } from './components/feature/MotorRefracao'
import { Perfis } from './components/feature/Perfis'
import { Recursos } from './components/feature/Recursos'
import { Creditos } from './components/feature/Creditos'
import { Planos } from './components/feature/Planos'
import { ChamadaFinal } from './components/feature/ChamadaFinal'

/**
 * Landing page do Prisma - a vitrine pública.
 *
 * As telas definitivas de aluno, professor, diretor e login vivem em
 * `app/` e sao servidas em `/app/` apos a sincronizacao.
 */
function Landing() {
  return (
    <>
      <a
        href="#conteudo"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-60 focus:rounded-lg focus:bg-primaria focus:px-4 focus:py-2 focus:text-white"
      >
        Pular para o conteúdo
      </a>

      <Header />

      <main id="conteudo">
        <Hero />
        <MotorRefracao />
        <Perfis />
        <Recursos />
        <Creditos />
        <Planos />
        <ChamadaFinal />

      </main>

      <Rodape />
    </>
  )
}

function Conteudo() {
  if (window.location.pathname === '/entrar') {
    window.location.replace('/app/login.html')
    return null
  }
  return <Landing />
}

function App() {
  return <Conteudo />
}

export default App
