/* Conteudo de demonstracao das conversas iniciais do tutor - uma por
   materia, cada uma exercitando um recurso diferente (quiz, citacao,
   chamada de ferramenta, diff) para a tela nunca ficar vazia na
   primeira visita. Nao e logica de produto, so dado; fica fora de
   `loja.js` para a loja continuar sem saber o que e "conteudo de
   demonstracao" versus "conversa real". */
import { criarConversa, criarMensagem } from './modelo.js';

function msg(papel, texto, extra) {
  return criarMensagem(Object.assign({ papel: papel, texto: texto }, extra || {}));
}

function conversaPortugues() {
  return criarConversa({
    materiaId: 'portugues',
    titulo: 'Orações reduzidas',
    mensagens: [
      msg('ai', 'Adjetiva ou adverbial? _"Apesar de você…"_ — que tipo é?'),
      msg('user', 'Adverbial! Indica concessão, né?'),
      msg('ai', 'Certo. Vamos para o ENEM ou revisamos **orações reduzidas**?'),
      msg('user', 'Vai de ENEM. Se eu errar, a gente volta pra teoria.'),
      msg('ai', 'Buscando um exemplo real no seu material…', {
        ferramentas: [{ nome: 'Prova_Portugues_2023.pdf', status: 'concluida' }],
      }),
      msg('ai', 'Em _"Caminhando contra o vento, sem lenço e sem documento"_, a oração destacada é reduzida de gerúndio [1].', {
        tipo: 'quiz',
        opcoes: ['causa', 'modo', 'condição', 'tempo'],
        corretaIndice: 2,
        citacoes: [{ numero: 1, fonte: 'Prova_Portugues_2023.pdf', trecho: 'Questão 14 — sintaxe do período composto' }],
        tempoRespostaMs: 1240,
      }),
    ],
  });
}

function conversaMatematica() {
  return criarConversa({
    materiaId: 'matematica',
    titulo: 'Função do 2º grau',
    mensagens: [
      msg('user', 'Como eu resolvo x² - 5x + 6 = 0?'),
      msg(
        'ai',
        'Dá para fatorar direto, sem fórmula de Bhaskara. Precisamos de dois números que somem **5** e multipliquem **6**: são o 2 e o 3.\n\n' +
          '```text\n' +
          'x² - 5x + 6 = 0\n' +
          '(x - 2)(x - 3) = 0\n' +
          'x = 2  ou  x = 3\n' +
          '```\n\n' +
          'Repare que sempre que o coeficiente de `x²` é 1, vale a pena tentar fatorar antes de partir pra fórmula — é mais rápido e erra menos.',
        { tempoRespostaMs: 2180 },
      ),
    ],
  });
}

function conversaHistoria() {
  return criarConversa({
    materiaId: 'historia',
    titulo: 'Era Vargas',
    mensagens: [
      msg('user', 'Resume a Era Vargas pra mim, os três períodos.'),
      msg('ai', 'Consultando seus flashcards de História…', {
        ferramentas: [{ nome: 'Era Vargas — flashcards', status: 'concluida' }],
      }),
      msg(
        'ai',
        'Três fases, cada uma com uma lógica de poder diferente [1]:\n\n' +
          '- **Governo Provisório (1930–1934)** — Vargas chega pela Revolução de 30, governa por decreto\n' +
          '- **Constitucional (1934–1937)** — eleito indiretamente, tensão crescente com integralistas e comunistas\n' +
          '- **Estado Novo (1937–1945)** — golpe, ditadura, censura e o nascimento da CLT\n\n' +
          'Se quiser, monto 5 questões estilo ENEM só sobre a transição entre a fase constitucional e o golpe do Estado Novo.',
        {
          citacoes: [{ numero: 1, fonte: 'Era Vargas — flashcards', trecho: '32 cartões · revisado em 30/07' }],
          tempoRespostaMs: 1890,
        },
      ),
    ],
  });
}

function conversaRedacao() {
  return criarConversa({
    materiaId: 'redacao',
    titulo: 'Correção de parágrafo',
    mensagens: [
      msg('user', 'Corrige esse parágrafo da minha introdução:\n\n"A tecnologia vem crescendo cada vez mais nos últimos tempos e isso afeta muito a vida das pessoas em vários aspectos."'),
      msg(
        'ai',
        'Está correto, mas genérico demais para uma introdução de nota alta — falta um repertório concreto e uma tese clara. Veja o que eu mudaria:\n\n' +
          '```diff\n' +
          '- A tecnologia vem crescendo cada vez mais nos últimos tempos e isso\n' +
          '- afeta muito a vida das pessoas em vários aspectos.\n' +
          '+ A aceleração da transformação digital, intensificada pela\n' +
          '+ popularização da inteligência artificial, reconfigura práticas\n' +
          '+ sociais que vão do trabalho à educação — e evidencia a urgência\n' +
          '+ de discutir seus limites éticos.\n' +
          '```\n\n' +
          'A diferença: a segunda versão nomeia **o que** mudou (IA, transformação digital) e já aponta **para onde** o texto vai (limites éticos) — isso é a tese.',
        { tempoRespostaMs: 2640 },
      ),
    ],
  });
}

export function conversasSemente() {
  return [conversaPortugues(), conversaMatematica(), conversaHistoria(), conversaRedacao()];
}
