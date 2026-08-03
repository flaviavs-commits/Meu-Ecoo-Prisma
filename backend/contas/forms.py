from django import forms

from .models import Usuario


class UsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirmacao", widget=forms.PasswordInput, required=False)

    class Meta:
        model = Usuario
        fields = ("email", "first_name", "instituicao", "perfil", "password1", "password2")

    def clean(self):
        dados = super().clean()
        if dados.get("password1") != dados.get("password2"):
            raise forms.ValidationError("As senhas nao conferem.")
        return dados

    def save(self, commit=True):
        usuario = super().save(commit=False)
        senha = self.cleaned_data.get("password1")
        if senha:
            usuario.set_password(senha)
        else:
            usuario.set_unusable_password()
        if commit:
            usuario.save()
        return usuario


class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = (
            "email", "first_name", "last_name", "instituicao", "perfil", "ativo", "is_active",
            "is_staff", "is_superuser", "groups", "user_permissions", "data_nascimento",
            "responsavel_nome", "responsavel_contato", "consentimento_responsavel_em",
        )
