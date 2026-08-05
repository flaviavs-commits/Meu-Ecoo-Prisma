from django import forms

from limites.models import PlanoInstitucional


class InstituicaoForm(forms.Form):
    """Valida os dados usados para abrir uma nova instituicao."""

    nome = forms.CharField(label="Nome", max_length=200)
    documento = forms.CharField(label="Documento", max_length=18)
    plano = forms.ModelChoiceField(
        label="Plano por conta",
        queryset=PlanoInstitucional.objects.filter(ativo=True).order_by("preco_por_conta"),
    )

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()
        if not nome:
            raise forms.ValidationError("Informe o nome da instituicao.")
        return nome

    def clean_documento(self):
        documento = self.cleaned_data["documento"].strip()
        if not documento:
            raise forms.ValidationError("Informe o documento da instituicao.")
        return documento
