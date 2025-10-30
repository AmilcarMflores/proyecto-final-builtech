from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Persona

# Formulario de registro
class RegistroForm(forms.ModelForm):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Persona
        fields = ['ci', 'nombre', 'apellido', 'telefono', 'tipo']

# Formulario de login
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario o Email")
    password = forms.CharField(widget=forms.PasswordInput)

