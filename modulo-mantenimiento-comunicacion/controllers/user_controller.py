from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from views import user_view
from models.user_model import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    if current_user.is_authenticated:
        # Redirige a la nueva ruta 'user.profile'
        return redirect(url_for('user.profile', id=current_user.id))
    return redirect(url_for('user.login'))

@user_bp.route('/register', methods=['GET', 'POST'])
def create_user():
    if request.method == "POST":
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        check_password = request.form.get('check_password') # Capturar la confirmación
        role = request.form.get('role', 'user')
        existing_user = User.get_by_email(email)

        # Validación 1: Correo ya registrado
        if existing_user:
            flash('El correo electrónico ya está registrado.', 'danger')
            return redirect(url_for('user.create_user'))

        # Validación 2: Contraseñas no coinciden (esto faltaba)
        if password != check_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('user.create_user'))
        
        # El constructor User ya llama a set_password(password), por lo que no es necesario
        new_user = User(first_name, last_name, email, password, role=role)
        new_user.save()
        flash('Usuario registrado exitosamente. Por favor, inicie sesión.', 'success')
        return redirect(url_for('user.login')) # Usamos user.login

    # Si es GET, se renderiza la vista
    return user_view.register()

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile', id=current_user.id))
        
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        # Cambiamos la variable de 'email' a 'user'
        user = User.get_by_email(email)
        
        # Usamos el método check_password del modelo y la nueva variable 'user'
        if user and user.check_password(password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            # Redirige a la nueva ruta 'user.profile'
            return redirect(url_for('user.profile', id=user.id))
            
        flash('Correo o contraseña incorrectos.', 'danger')
        return redirect(url_for('user.login'))
        
    return user_view.login()

# ************ RUTA DE PERFIL AGREGADA ************
@user_bp.route('/profile/<int:id>')
@login_required # Requiere que el usuario esté logueado
def profile(id):
    # Opcional: prevenir que un usuario vea el perfil de otro
    if current_user.id != id:
        flash('No tienes permiso para ver este perfil.', 'danger')
        return redirect(url_for('user.index'))
    
    user = User.get_by_id(id)
    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('user.index'))
        
    return user_view.perfil(user) # Llama a la vista 'perfil' que renderiza 'base.html'

# Ruta para cerrar sesión
@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('user.login')) # Redirige a la página de login