import { Header } from './components/layout/Header'
import { Rodape } from './components/layout/Rodape'
import { Hero } from './components/feature/Hero'
import { MotorRefracao } from './components/feature/MotorRefracao'
import { Perfis } from './components/feature/Perfis'
import { Recursos } from './components/feature/Recursos'
import { Creditos } from './components/feature/Creditos'
import { Planos } from './components/feature/Planos'
import { ChamadaFinal } from './components/feature/ChamadaFinal'
import { PaginaLogin } from './components/auth/PaginaLogin'
import { AutenticacaoProvider } from './auth/contexto'

/**
 * Landing page do Prisma - a vitrine pública.
 *
 * As telas estaticas de aluno, professor e diretor sao derivadas de
 * `mockup/` e servidas em `/app/`. O "Entrar" abre o fluxo autenticado;
 * a protecao das telas por perfil sera a proxima camada.
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
  return window.location.pathname === '/entrar' ? <PaginaLogin /> : <Landing />
}

function App() {
  return (
    <AutenticacaoProvider>
      <Conteudo />
    </AutenticacaoProvider>
  )
}

export default App
