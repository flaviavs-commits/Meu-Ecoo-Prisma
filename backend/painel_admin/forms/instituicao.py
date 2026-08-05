from decimal import Decimal

from django import forms


class InstituicaoForm(forms.Form):
    """Valida os dados usados para abrir uma nova instituicao."""

    nome = forms.CharField(label="Nome", max_length=200)
    documento = forms.CharField(label="Documento", max_length=18)
    creditos_iniciais = forms.DecimalField(
        label="Creditos iniciais",
        max_digits=14,
        decimal_places=4,
        min_value=Decimal("0"),
        help_text="Use zero se a instituicao receber creditos depois.",
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
