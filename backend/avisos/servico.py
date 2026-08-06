"""Regra de quem envia e de quem lê um aviso."""
from django.db.models import Q

from .excecoes import AvisoPermissaoError
from .models import Aviso


def enviar_aviso(*, turma, autor, titulo, mensagem, prazo_entrega=None):
    """Publica um comunicado para os alunos da turma.

    Envia quem leciona nela - titular ou corpo docente - e o diretor da
    instituicao, que responde por todas as turmas da escola.
    """
    if autor.instituicao_id is None or autor.instituicao_id != turma.instituicao_id:
        raise AvisoPermissaoError("Turma fora da instituicao.", codigo="fora_da_instituicao")

    if autor.perfil == "PROFESSOR":
        if not turma.leciona(autor):
            raise AvisoPermissaoError("Professor nao leciona nesta turma.")
    elif autor.perfil != "DIRETOR":
        raise AvisoPermissaoError("Perfil sem permissao para enviar avisos.")

    titulo = str(titulo or "").strip()
    mensagem = str(mensagem or "").strip()
    if not titulo or not mensagem:
        raise ValueError("Titulo e mensagem sao obrigatorios.")

    return Aviso.objects.create(
        instituicao_id=turma.instituicao_id,
        turma=turma,
        autor=autor,
        titulo=titulo,
        mensagem=mensagem,
        prazo_entrega=prazo_entrega,
    )


def avisos_visiveis(usuario):
    """Avisos que a conta pode ler, pelo escopo do seu perfil."""
    if usuario.instituicao_id is None:
        return Aviso.objects.none()

    base = Aviso.objects.filter(instituicao_id=usuario.instituicao_id)
    if usuario.perfil == "ALUNO":
        # So as turmas em que a matricula esta aberta.
        return base.filter(
            turma__matriculas__aluno_id=usuario.id,
            turma__matriculas__saiu_em__isnull=True,
        ).distinct()
    if usuario.perfil == "PROFESSOR":
        return base.filter(
            Q(turma__professor_responsavel_id=usuario.id)
            | Q(turma__professores=usuario.id)
        ).distinct()
    if usuario.perfil == "DIRETOR":
        return base
    return Aviso.objects.none()
