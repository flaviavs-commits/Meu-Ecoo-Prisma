from django import forms


class InstituicaoEdicaoForm(forms.Form):
    """Valida a edição administrativa de uma instituição escolar."""

    nome = forms.CharField(label="Nome", max_length=200)
    documento = forms.CharField(label="Documento", max_length=18)

    def clean_nome(self):
        nome = self.cleaned_data["nome"].strip()
        if not nome:
            raise forms.ValidationError("Informe o nome da instituição.")
        return nome

    def clean_documento(self):
        documento = self.cleaned_data["documento"].strip()
        if not documento:
            raise forms.ValidationError("Informe o documento da instituição.")
        return documento
