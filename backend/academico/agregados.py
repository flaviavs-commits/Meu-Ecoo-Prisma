from decimal import Decimal

from django.db.models import Avg

from .models import Nota


def media_da_turma(turma, *, disciplina=None):
    notas = Nota.objects.filter(turma=turma)
    if disciplina:
        notas = notas.filter(disciplina=disciplina)
    return notas.aggregate(media=Avg("valor"))["media"] or Decimal("0")
