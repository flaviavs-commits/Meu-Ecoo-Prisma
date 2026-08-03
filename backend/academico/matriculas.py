from django.contrib.auth import get_user_model

from .models import Matricula


def matricular(*, turma, aluno, criado_por):
    if turma.instituicao_id != aluno.instituicao_id:
        raise MatriculaError("Matricula fora da instituicao.", codigo="fora_da_instituicao")
    if aluno.perfil != "ALUNO" or criado_por.perfil != "DIRETOR":
        raise MatriculaError("Somente diretor pode matricular aluno.", codigo="sem_permissao")
    return Matricula.objects.create(turma=turma, aluno=aluno)


def listar_alunos(turma):
    return get_user_model().objects.filter(
        matriculas__turma=turma, matriculas__saiu_em__isnull=True
    ).order_by("id")


class MatriculaError(Exception):
    def __init__(self, mensagem, *, codigo):
        super().__init__(mensagem)
        self.codigo = codigo
