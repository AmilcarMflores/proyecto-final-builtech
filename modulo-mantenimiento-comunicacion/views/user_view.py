# app/views/user_view.py

from flask import render_template, url_for
from flask_login import current_user

def register():
    return render_template(
        'register.html',
        title = "Registro",
        current_user = current_user,
    )

def login():
    return render_template(
        'login.html',
        title = "Inicio de Sesión",
        current_user = current_user,
    )

# No necesita cambios, ya estaba lista.
def perfil(user):
  return render_template(
    "base.html",
    title="Perfil de Usuario", # Título más descriptivo
    current_user=current_user,
    user=user, # Pasa el objeto 'user' que es usado en base.html
    )