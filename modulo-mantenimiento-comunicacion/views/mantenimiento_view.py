from flask import render_template, url_for

def crear_ticket():
    return render_template(
        "maintenance/crear.html",  # Ruta corregida
        title="Crear ticket"
    )

def list_ticket(tickets):
    return render_template(
        "maintenance/list_tickets.html",  # Ruta corregida
        tickets=tickets,
        title="Lista de tickets"
    )

def update_ticket_ini(ticket):
    return render_template(
        "maintenance/actualizar_ini.html",  # Ruta corregida
        title="Actualizar ticket",
        ticket=ticket
    )

def update_ticket_fin(ticket):
    return render_template(
        "maintenance/actualizar_fin.html",  # Ruta corregida
        title="Finalizar ticket",
        ticket=ticket
    )

def generate_ticket(ticket):
    return render_template(
        "maintenance/generate_ticket.html",  # Ruta corregida
        title="Ticket",
        ticket=ticket,
        download_url=url_for('mantenimiento.download_report', id=ticket.id_mantenimiento)
    )