from flask import Blueprint, render_template, request, jsonify
from models.chat_model import ChatMessage, Notification
from models.mantenimiento_model import Mantenimiento
from flask_login import login_required, current_user
from utils.decorators import role_required

chat_bp = Blueprint("chat", __name__, url_prefix="/comunicacion")

@chat_bp.route("/chat")
@login_required
def chat_general():
    """Chat general del sistema"""
    username = current_user.first_name if current_user.is_authenticated else 'Anónimo'
    return render_template(
        "comunicacion/chat.html",  # Ruta corregida
        title="Chat General",
        current_username=username 
    )

@chat_bp.route("/chat/ticket/<int:ticket_id>")
@login_required
def chat_ticket(ticket_id):
    """Chat específico de un ticket"""
    ticket = Mantenimiento.get_by_id(ticket_id)
    if not ticket:
        return "Ticket no encontrado", 404
    
    username = current_user.first_name if current_user.is_authenticated else 'Anónimo'
    
    return render_template(
        "comunicacion/chat_ticket.html",  # Ruta corregida
        title=f"Chat - Ticket #{ticket_id}",
        ticket=ticket,
        current_username=username 
    )

@chat_bp.route("/notificaciones")
@role_required('admin')
def notificaciones():
    """Ver todas las notificaciones"""
    notificaciones = Notification.get_all()
    return render_template(
        "comunicacion/notificaciones.html",  # Ruta corregida
        title="Notificaciones",
        notificaciones=notificaciones
    )

@chat_bp.route("/api/notificaciones/no-leidas")
@login_required
def notificaciones_no_leidas():
    """API: Obtener notificaciones no leídas"""
    if current_user.has_role('admin'):
        notificaciones = Notification.get_no_leidas()
        return jsonify({
            'count': len(notificaciones),
            'notificaciones': [n.to_dict() for n in notificaciones]
        })
    return jsonify({'count': 0, 'notificaciones': []})


@chat_bp.route("/api/notificaciones/<int:id>/marcar-leida", methods=["POST"])
@login_required
def marcar_notificacion_leida(id):
    """API: Marcar notificación como leída"""
    if not current_user.has_role('admin'):
        return jsonify({'success': False, 'error': 'Permiso denegado'}), 403
        
    notificacion = Notification.query.get(id)
    if notificacion:
        notificacion.marcar_leido()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Notificación no encontrada'}), 404