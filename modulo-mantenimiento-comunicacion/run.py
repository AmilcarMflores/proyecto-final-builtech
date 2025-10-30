# app/run.py

from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from controllers import mantenimiento_controller, comunicacion_controller
from controllers import user_controller
from database import db
from socket_events import register_socket_events
from models.user_model import User

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buildtech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave-secreta'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Inicializar Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Crear directorio de uploads si no existe
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'evidencias')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

db.init_app(app)
app.register_blueprint(user_controller.user_bp)
app.register_blueprint(mantenimiento_controller.mantenimiento_bp)
app.register_blueprint(comunicacion_controller.comunicacion_bp)

# Registrar eventos de Socket.IO
register_socket_events(socketio)

with app.app_context():
    db.create_all()
    print("\n" + "="*60)
    print("✓ Base de datos y tablas creadas correctamente.")
    print("✓ Servidor corriendo en: http://127.0.0.1:5000")
    print("="*60)
    print("\n📋 RUTAS PRINCIPALES:")
    print("   🏠 Inicio:          http://127.0.0.1:5000/")
    print("   📝 Lista tickets:   http://127.0.0.1:5000/mantenimiento")
    print("   ➕ Crear ticket:    http://127.0.0.1:5000/mantenimiento/crear")
    print("\n💬 COMUNICACIÓN:")
    print("   💬 Chat:            http://127.0.0.1:5000/comunicacion/chat")
    print("   📢 Avisos:          http://127.0.0.1:5000/comunicacion/avisos")
    print("   📝 Quejas:          http://127.0.0.1:5000/comunicacion/quejas")
    print("   🔔 Notificaciones:  http://127.0.0.1:5000/comunicacion/notificaciones")
    print("="*60 + "\n")

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)