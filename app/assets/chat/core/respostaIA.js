/* Banco de respostas do tutor para o chat AO VIVO (nao as conversas de
   semente). Sem gateway de IA neste repositorio, a "geracao" e um
   roteiro que roda em ciclo - mas o roteiro inclui markdown de verdade
   (negrito, lista, bloco de codigo, citacao) para o streaming/render
   nunca parecer so texto puro na demonstracao. */
const BANCO = [
  { texto: 'Boa. Repare que o conectivo muda o valor da oração — testa trocar por "embora" e vê se o sentido se mantém.' },
  { texto: 'Quase. **Reduzidas** não têm conectivo explícito: o verbo vem no infinitivo, gerúndio ou particípio. Qual dos três aparece aí?' },
  {
    texto: 'Isso mesmo. Três formas de fixar esse tópico:\n\n- Reler a definição\n- Resolver 3 questões parecidas\n- Seguir para o próximo assunto\n\nQual prefere?',
  },
  {
    texto: 'Vou anotar essa dúvida no seu contexto para retomarmos na próxima sessão [1].',
    citacoes: [{ numero: 1, fonte: 'Registro de sessão', trecho: 'salvo automaticamente ao final da conversa' }],
  },
  {
    texto: 'Aqui está um jeito rápido de organizar isso:\n\n```text\npasso 1 — identificar o verbo\npasso 2 — classificar a oração\npasso 3 — confirmar pelo sentido\n```\n\nQuer aplicar isso no próximo exemplo?',
  },
  {
    texto: 'Antes de responder, deixa eu confirmar no seu material…',
    ferramentas: [{ nome: 'Aula_oracoes_reduzidas.docx', status: 'concluida' }],
  },
];
let indice = 0;

export function gerarResposta() {
  const escolhida = BANCO[indice % BANCO.length];
  indice++;
  return {
    texto: escolhida.texto,
    citacoes: escolhida.citacoes || [],
    ferramentas: escolhida.ferramentas || [],
  };
}
