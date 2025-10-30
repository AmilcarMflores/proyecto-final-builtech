from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class RegistroForm(forms.Form):
    ci = forms.CharField(max_length=20, label="CI")
    nombre = forms.CharField(max_length=100, label="Nombre")
    apellido = forms.CharField(max_length=100, label="Apellido")
    telefono = forms.CharField(max_length=15, required=False, label="Teléfono")
    tipo = forms.ChoiceField(
        choices=[('propietario', 'Propietario'), ('inquilino', 'Inquilino')],
        label="Tipo"
    )
    username = forms.CharField(max_length=150, label="Usuario")
    email = forms.EmailField(label="Correo")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password is None:
            return password
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
