class AvisoPermissaoError(PermissionError):
    """Quem enviou o aviso não leciona na turma indicada."""

    def __init__(self, mensagem, *, codigo="sem_permissao"):
        super().__init__(mensagem)
        self.codigo = codigo
