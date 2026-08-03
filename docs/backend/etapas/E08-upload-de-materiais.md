# E08 - Upload de materiais

> **Status:** NAO INICIADA · **Responsavel:** _(assine ao pegar)_
> **Depende de:** E02 · **Destrava:** E10
>
> ⚠️ **Escreva na secao 8 enquanto trabalha, nao no fim.** Regras:
> [`../PROTOCOLO-DO-AGENTE.md`](../PROTOCOLO-DO-AGENTE.md)

## 1. Objetivo

Permitir que professor e aluno enviem arquivo (PDF, imagem, audio) e que o
sistema guarde, sirva e isole esses arquivos com seguranca.

Pode comecar cedo: depende so de E02, entao roda em paralelo com E03-E07.

## 2. Pre-requisitos

- E02 `CONCLUIDA`
- [`../contratos/LGPD-E-DADOS-SENSIVEIS.md`](../contratos/LGPD-E-DADOS-SENSIVEIS.md)

## 3. Escopo

**Entra:** model de arquivo, upload validado, armazenamento em disco,
servir com controle de acesso, limites.

**Nao entra:** armazenamento em nuvem (S3/MinIO), extracao de texto do PDF e
geracao de audio - esta ultima vem dos repositorios satelites
([E13](E13-api-nos-repos-satelites.md)).

## 4. Decisao ja travada

**Arquivo vai para disco, do jeito mais simples.** Decidido explicitamente,
sabendo do limite: disco nao e compartilhado entre multiplas instancias da API.
Se um dia a API escalar horizontalmente, migra-se para armazenamento em nuvem.

Consequencia que voce **deve** respeitar: escreva o acesso a arquivo atras de um
**adaptador**, usando o sistema de storage do Django. A migracao futura tem que
ser troca de configuracao, nao reescrita.

No Railway, disco que sobrevive a redeploy exige um **Volume** montado - isso e
configurado na [E12](E12-infra-railway-e-deploy.md). Sem volume, o arquivo some
no proximo deploy. Combine com quem estiver na E12 e registre.

## 5. Como fazer

### 5.1 Model `Arquivo`

| Campo | Papel |
|-------|-------|
| `instituicao` | FK obrigatoria (base de E02) |
| `enviado_por` | FK de usuario |
| `nome_original` | Como o usuario chamou - **nunca** usado como caminho |
| `arquivo` | `FileField` |
| `tipo_mime` | Detectado pelo **conteudo**, nao pela extensao |
| `tamanho_bytes` | Para limite e cota |
| `criado_em` | |

### 5.2 Caminho no disco - onde mora a maior armadilha

```text
midia/<instituicao_id>/<uuid>/<nome-normalizado>
```

Regras que nao se negociam:

- **Nunca** use o nome enviado pelo usuario direto no caminho. `../../etc/passwd`
  e `..\\` sao ataques de path traversal com decadas de idade e ainda funcionam.
- Gere sempre um `uuid` proprio para a pasta.
- Normalize o nome guardado (sem barra, sem `..`, sem caractere de controle,
  tamanho limitado).
- Separar por `instituicao_id` mantem o isolamento visivel tambem no disco.

### 5.3 Validacao - por conteudo, nao por extensao

Renomear `virus.exe` para `trabalho.pdf` e o ataque mais simples que existe.

- valide o **tipo real** pelo conteudo (assinatura do arquivo), nao pela
  extensao nem pelo `Content-Type` enviado pelo cliente - os dois sao dados do
  atacante;
- lista **branca** de tipos aceitos (PDF, PNG, JPEG, MP3, DOCX...), nunca lista
  negra;
- limite de tamanho por arquivo, aplicado **no servidor** - o limite do
  frontend nao existe para quem chama a API direto;
- limite de tamanho total por instituicao (cota), para um cliente nao encher o
  disco de todos.

SVG merece atencao: e XML, pode conter script, e vira XSS se servido inline.
Se aceitar SVG, sirva sempre como download, nunca inline.

### 5.4 Servir o arquivo - com permissao

Arquivo **nao** pode ser servido por URL publica adivinhavel. Nota, prova e
trabalho de aluno nao sao conteudo publico.

O download passa por uma view que:

1. autentica;
2. confere que o arquivo e da instituicao do usuario - se nao for, **404**;
3. confere permissao sobre aquele arquivo (E04);
4. so entao entrega.

Sempre com `Content-Disposition: attachment` e
`X-Content-Type-Options: nosniff`. Servir conteudo enviado por usuario inline no
mesmo dominio da aplicacao e vetor classico de XSS.

### 5.5 TDD - ordem sugerida

1. Upload valido guarda o arquivo e cria o registro.
2. Arquivo com nome `../../../etc/passwd` nao escapa da pasta.
3. `.exe` renomeado para `.pdf` e recusado (validacao por conteudo).
4. Arquivo acima do limite e recusado.
5. Instituicao acima da cota e recusada.
6. Download por usuario de outra instituicao -> 404.
7. Download sem autenticacao -> 401.
8. Resposta traz `attachment` e `nosniff`.
9. Dois arquivos com o mesmo nome nao se sobrescrevem.

## 6. Contrato de saida

- `Arquivo` migrado, isolado por instituicao
- upload validado por conteudo, com limite e cota
- download autenticado e autorizado
- acesso a storage atras de adaptador - migravel para nuvem por configuracao

E10 usa este `Arquivo` para anexar material e prova; nao cria armazenamento
proprio.

## 7. Riscos e pendencias

| Risco | Mitigacao |
|-------|-----------|
| Path traversal | UUID + normalizacao. Teste 2. |
| Executavel disfarcado | Validacao por conteudo + lista branca |
| XSS por arquivo servido inline | `attachment` + `nosniff`; SVG so como download |
| Arquivo perdido em redeploy | Volume no Railway (E12). **Confirme, nao presuma.** |
| Disco cheio derrubando o servico | Cota por instituicao |
| Antivirus | Nao ha varredura. **Registre como risco aceito** e limitacao conhecida. |

## 8. Diario de execucao - PREENCHA ENQUANTO TRABALHA

> Formato: `- [AAAA-MM-DD] o que fez - por que - como validou`
>
> Ao pegar: status para `EM ANDAMENTO`, assine, atualize
> [`../README.md`](../README.md).

_(vazio - primeira entrada e sua)_

## 9. Criterio de pronto

- [ ] Os 9 testes do item 5.5 passam - saida real no diario
- [ ] Teste de path traversal existe e passa
- [ ] Validacao por conteudo verificada com arquivo renomeado de verdade
- [ ] Download de outra instituicao responde 404
- [ ] Storage atras de adaptador - troca por configuracao
- [ ] Necessidade de Volume comunicada a quem faz a E12, registrada no diario
- [ ] Ausencia de antivirus registrada como risco aceito
- [ ] Nenhum arquivo passa de 300 linhas
- [ ] Commit feito, so com arquivos desta etapa
