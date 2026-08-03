class EscopoInstituicaoMixin:
    """Filtra a queryset da view para a instituicao do usuario autenticado."""

    campo_instituicao = "instituicao"

    def get_queryset(self):
        queryset = super().get_queryset()
        instituicao_id = getattr(self.request.user, "instituicao_id", None)
        if not instituicao_id:
            return queryset.none()
        return queryset.filter(**{f"{self.campo_instituicao}_id": instituicao_id})
