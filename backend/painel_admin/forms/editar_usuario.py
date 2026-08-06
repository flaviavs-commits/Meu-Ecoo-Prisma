from django import forms

from contas.models import (
    CODIGO_PROVEDORA,
    CODIGO_PRISMA,
    Instituicao,
    Perfil,
    TipoInstituicao,
)

from .conta_teste import PERFIS_ACADEMICOS


class UsuarioEdicaoForm(forms.Form):
    """Valida a edição cross-tenant de uma conta pelo provider."""

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
        # Conta da equipe nao troca de tier por este formulario: o campo fica
        # travado na propria instituicao interna e no proprio perfil.
        if alvo.is_superuser:
            self._travar_na_equipe(CODIGO_PROVEDORA, TipoInstituicao.PROVEDORA, Perfil.PROVIDER)
        elif alvo.perfil == Perfil.ADMINISTRADOR:
            self._travar_na_equipe(CODIGO_PRISMA, TipoInstituicao.PRISMA, Perfil.ADMINISTRADOR)

    def _travar_na_equipe(self, codigo, tipo, perfil):
        self.fields["instituicao"].queryset = Instituicao.objects.filter(
            ativa=True, codigo=codigo, tipo=tipo
        ).order_by("nome")
        self.fields["perfil"].choices = ((perfil, perfil.label),)

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_first_name(self):
        nome = self.cleaned_data["first_name"].strip()
        if not nome:
            raise forms.ValidationError("Informe o nome da conta.")
        return nome
