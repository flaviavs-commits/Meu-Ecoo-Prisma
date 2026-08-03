class ConteudoEstadoError(Exception):
    """Estado oficial so pode ser alcancado pelo servico de oficializacao."""


class ConteudoConfirmacaoError(Exception):
    codigo = "confirmacao_obrigatoria"


class ConteudoSemQuestoesError(Exception):
    codigo = "prova_sem_questoes"


class ConteudoConflitoError(Exception):
    codigo = "conteudo_ja_oficial"


class ConteudoPermissaoError(Exception):
    codigo = "sem_permissao"


class ConteudoForaDaInstituicaoError(Exception):
    codigo = "fora_da_instituicao"
