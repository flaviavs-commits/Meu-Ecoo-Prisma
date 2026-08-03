from django.conf import settings

from .models import ClasseTarefa


def modelo_para_classe(classe_tarefa: ClasseTarefa) -> str:
    """Resolve o modelo somente a partir do mapa de configuracao."""
    chave = getattr(classe_tarefa, "value", classe_tarefa)
    try:
        return settings.IA_MODELOS[chave]
    except KeyError as erro:
        raise ValueError(f"Classe de tarefa sem modelo configurado: {chave}") from erro
