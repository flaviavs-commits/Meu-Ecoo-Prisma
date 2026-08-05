from django import forms

from contas.models import Instituicao, Perfil, TipoInstituicao

from .conta_teste import PERFIS_ACADEMICOS


class UsuarioEdicaoForm(forms.Form):
    """Valida a edição cross-tenant de uma conta pelo mantenedor."""

    email = forms.EmailField(label="E-mail")
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150, required=False)
    instituicao = forms.ModelChoiceField(
        label="Instituição",
        queryset=Instituicao.objects.filter(ativa=True).order_by("nome"),
    )
    perfil = forms.ChoiceField(label="Perfil", choices=PERFIS_ACADEMICOS)
    ativo = forms.BooleanField(label="Conta ativa", required=False)

    def __init__(self, *, alvo, **kwargs):
        super().__init__(**kwargs)
        self.alvo = alvo
        if alvo.is_superuser:
            self.fields["instituicao"].queryset = Instituicao.objects.filter(
                ativa=True,
                codigo="VITIS_SOULS",
                tipo=TipoInstituicao.MANTENEDORA,
            ).order_by("nome")
            self.fields["perfil"].choices = (
                (Perfil.MANTENEDOR, Perfil.MANTENEDOR.label),
            )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_first_name(self):
        nome = self.cleaned_data["first_name"].strip()
        if not nome:
            raise forms.ValidationError("Informe o nome da conta.")
        return nome
