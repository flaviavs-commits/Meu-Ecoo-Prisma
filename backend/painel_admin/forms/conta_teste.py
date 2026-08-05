from django import forms
from django.contrib.auth.password_validation import validate_password

from contas.models import Instituicao, Perfil, Usuario


class ContaTesteForm(forms.Form):
    """Valida uma conta academica com senha para testes manuais."""

    email = forms.EmailField(label="E-mail")
    first_name = forms.CharField(label="Nome", max_length=150)
    last_name = forms.CharField(label="Sobrenome", max_length=150, required=False)
    instituicao = forms.ModelChoiceField(
        label="Instituicao",
        queryset=Instituicao.objects.filter(ativa=True).order_by("nome"),
        empty_label="Selecione uma instituicao",
    )
    perfil = forms.ChoiceField(label="Perfil", choices=Perfil.choices)
    password1 = forms.CharField(
        label="Senha",
        min_length=10,
        widget=forms.PasswordInput,
        help_text="Use pelo menos 10 caracteres.",
    )
    password2 = forms.CharField(label="Confirmacao", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ja existe uma conta com este e-mail.")
        return email

    def clean_first_name(self):
        nome = self.cleaned_data["first_name"].strip()
        if not nome:
            raise forms.ValidationError("Informe o nome da conta.")
        return nome

    def clean_perfil(self):
        perfil = self.cleaned_data["perfil"]
        if perfil not in Perfil.values:
            raise forms.ValidationError("Selecione um perfil academico valido.")
        return perfil

    def clean(self):
        dados = super().clean()
        senha = dados.get("password1")
        confirmacao = dados.get("password2")
        if senha and confirmacao and senha != confirmacao:
            self.add_error("password2", "As senhas nao conferem.")
        if senha:
            usuario = Usuario(
                email=dados.get("email", ""),
                first_name=dados.get("first_name", ""),
                last_name=dados.get("last_name", ""),
            )
            try:
                validate_password(senha, user=usuario)
            except forms.ValidationError as erro:
                self.add_error("password1", erro)
        return dados
