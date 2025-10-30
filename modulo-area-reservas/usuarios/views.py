from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Persona, Usuario, Factura, Pago
from django.http import HttpResponse
from django.utils import timezone
from .models import Reserva, AreaComun,Pago
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm, LoginForm
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta,time
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(nombre_usuario=username)
            if check_password(password, usuario.contrasena_hash):
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre_usuario
                messages.success(request, f"Bienvenido {usuario.nombre_usuario} 👋")
                return redirect('home') 
            else:
                messages.error(request, "Contraseña incorrecta ❌")
        except Usuario.DoesNotExist:
            messages.error(request, "El usuario no existe ❌")

    return render(request, 'usuarios/login.html')



def logout_view(request):
    logout(request)
    return redirect('login')


def dashboard(request):
    return HttpResponse("Bienvenido al sistema. Login exitoso.")


def home(request):
    return render(request, "usuarios/home.html")

def reservas(request):
    print("Entra") 
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_id = request.session['usuario_id']

    if request.method == 'POST':
        try:
            id_area = int(request.POST.get('id_area'))
            fecha_res = request.POST.get('fecha_res')
            tipo_reserva = request.POST.get('tipo_reserva', 'dia')

            area = AreaComun.objects.get(id_area=id_area)
            area_nombre = area.nombre.lower()

            if area_nombre == 'parqueo':
                hora_ini = time(0, 0)
                duracion = 24
                numero_personas = None

                fechas = []
                if tipo_reserva == 'mes':
                    if " to " in fecha_res:
                        fechas_str = fecha_res.split(" to ")
                        start_date = datetime.strptime(fechas_str[0], "%Y-%m-%d").date()
                        end_date = datetime.strptime(fechas_str[1], "%Y-%m-%d").date()
                    else:
                        start_date = datetime.strptime(fecha_res, "%Y-%m-%d").date().replace(day=1)
                        next_month = start_date.replace(day=28) + timedelta(days=4)
                        end_date = next_month - timedelta(days=next_month.day)
                    delta = end_date - start_date
                    for i in range(delta.days + 1):
                        fechas.append(start_date + timedelta(days=i))
                else:
                    fechas = [datetime.strptime(fecha_res, "%Y-%m-%d").date()]

                for f in fechas:
                    reserva_creada = Reserva.objects.create(
                        id_usuario_id=usuario_id,
                        id_area_id=id_area,
                        fecha_res=f,
                        hora_ini=hora_ini,
                        duracion=duracion,
                        estado='pendiente',
                        numero_personas=numero_personas
                    )

                    Pago.objects.create(
                        id_factura=1,
                        id_reserva=reserva_creada,
                        id_nomina=None,
                        tipo='reserva',
                        monto=duracion * float(area.costo),
                        fecha_pago=timezone.now().date(),
                        referencia=f"Pago por reserva de {area.nombre}"
                    )

            else:
                hora_ini_str = request.POST.get('hora_ini')
                duracion_str = request.POST.get('duracion')
                numero_personas = request.POST.get('numero_personas') or None
                if not hora_ini_str or not duracion_str:
                    messages.error(request, "Debe seleccionar hora y duración para esta área.")
                    return redirect('reservas')

                duracion = int(duracion_str)
                fecha = datetime.strptime(fecha_res, "%Y-%m-%d").date()
                hora_ini = datetime.strptime(hora_ini_str, "%H:%M").time()

                reserva_creada = Reserva.objects.create(
                    id_usuario_id=usuario_id,
                    id_area_id=id_area,
                    fecha_res=fecha,
                    hora_ini=hora_ini,
                    duracion=duracion,
                    estado='pendiente',
                    numero_personas=numero_personas
                )

                Pago.objects.create(
                    id_factura=1,
                    id_reserva=reserva_creada,
                    id_nomina=None,
                    tipo='reserva',
                    monto=duracion * float(area.costo),
                    fecha_pago=timezone.now().date(),
                    referencia=f"Pago por reserva de {area.nombre}"
                )

            messages.success(request, "Reserva creada correctamente ✅")
            return redirect('home')

        except Exception as e:
            print(f"Error al crear reserva: {e}")
            messages.error(request, f"No se pudo crear la reserva: {e}")
            return redirect('reservas')
        pass

    reservas_usuario = Reserva.objects.filter(id_usuario_id=usuario_id).order_by('-fecha_res', '-hora_ini')

    areas = AreaComun.objects.all()

    return render(request, 'usuarios/reservas.html', {
        'areas': areas,
        'reservas_usuario': reservas_usuario})

def fechas_ocupadas(request, area_id):
    """Devuelve las fechas bloqueadas para el calendario según el área"""
    area = AreaComun.objects.get(id_area=area_id)
    reservas = Reserva.objects.filter(id_area_id=area_id)

    if area.nombre.lower() == 'parqueo':
        conteo_por_dia = {}
        for r in reservas:
            fecha = r.fecha_res
            conteo_por_dia[fecha] = conteo_por_dia.get(fecha, 0) + 1
        fechas_bloqueadas = [
            {"from": str(fecha), "to": str(fecha)}
            for fecha, cantidad in conteo_por_dia.items()
            if cantidad >= area.capacidad
        ]
        return JsonResponse(fechas_bloqueadas, safe=False)
    else:
        return JsonResponse([], safe=False)


def reservas_disponibles(request, area_id):
    reservas = Reserva.objects.filter(id_area_id=area_id)
    fechas_ocupadas = []

    for r in reservas:
        try:
            inicio = datetime.combine(r.fecha_res, r.hora_ini)
            fin = inicio + timedelta(minutes=r.duracion_min)
            fechas_ocupadas.append({
                "inicio": inicio.isoformat(),
                "fin": fin.isoformat()
            })
        except Exception as e:
            print(f"Error con la reserva {r.id}: {e}")

    return JsonResponse(fechas_ocupadas, safe=False)

def horarios_disponibles(request, area_id):
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        return JsonResponse([], safe=False)
    
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    
    horarios = []
    hora_inicio = datetime.combine(fecha, time(8,0))
    hora_fin = datetime.combine(fecha, time(20,0))
    while hora_inicio <= hora_fin:
        horarios.append(hora_inicio.strftime("%H:%M"))
        hora_inicio += timedelta(hours=1)

    reservas = Reserva.objects.filter(id_area_id=area_id, fecha_res=fecha)
    horarios_ocupados = set()
    for r in reservas:
        inicio_res = datetime.combine(r.fecha_res, r.hora_ini)
        fin_res = inicio_res + timedelta(hours=r.duracion)  # ← usar horas
        for h in horarios:
            h_dt = datetime.combine(fecha, datetime.strptime(h, "%H:%M").time())
            if inicio_res <= h_dt < fin_res:
                horarios_ocupados.add(h)

    horarios_libres = [h for h in horarios if h not in horarios_ocupados]

    return JsonResponse(horarios_libres, safe=False)

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id, id_usuario=request.session['usuario_id'])
    
    if request.method == "POST":
        reserva.fecha_res = request.POST.get('fecha_res')
        reserva.hora_ini = request.POST.get('hora_ini')
        reserva.duracion = int(request.POST.get('duracion'))
        reserva.numero_personas = request.POST.get('numero_personas') or None
        reserva.save()
        messages.success(request, "Reserva actualizada ✅")
        return redirect('reservas')
    
    return render(request, 'usuarios/editar_reserva.html', {'reserva': reserva})


def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id, id_usuario=request.session['usuario_id'])
    reserva.delete()
    messages.success(request, "Reserva eliminada ✅")
    return redirect('reservas')


def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id, id_usuario=request.session['usuario_id'])
    if request.method == "POST":
        fecha_str = request.POST.get('fecha_res')
        hora_str = request.POST.get('hora_ini')
        duracion_str = request.POST.get('duracion')
        personas_str = request.POST.get('numero_personas')
        
        try:
            reserva.fecha_res = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            reserva.hora_ini = datetime.strptime(hora_str, '%H:%M').time()
            reserva.duracion = int(duracion_str)
            reserva.numero_personas = int(personas_str) if personas_str else None
            
            
            reserva.save()
            
            messages.success(request, "Reserva actualizada correctamente ✅")
            return redirect('reservas')

        except Exception as e:
            messages.error(request, f"Error al actualizar la reserva: {e}")
            return redirect('reservas')
    return redirect('reservas')






def facturas_view(request):
    if 'usuario_id' not in request.session:
        messages.error(request, "Debes iniciar sesión para acceder a las facturas.")
        return redirect('login') 
        
    id_usuario_actual = request.session['usuario_id']

    try:
        usuario_actual = Usuario.objects.get(id_usuario=id_usuario_actual)
    except Usuario.DoesNotExist:
        messages.error(request, "Error interno: Usuario de sesión no encontrado.")
        return redirect('logout') # Forzar la salida

    facturas = Factura.objects.filter(id_usuario=usuario_actual).order_by('-fecha_emision')

    total_facturado = facturas.aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    
    total_pagado = Pago.objects.filter(id_factura__in=facturas.values('id_factura')).aggregate(Sum('monto'))['monto__sum'] or 0

    monto_pendiente = total_facturado - total_pagado
    
    context = {
        'facturas_usuario': facturas,
        'monto_pendiente': monto_pendiente,
    }
    
    return render(request, 'usuarios/facturas.html', context)

def modulo_financiero(request):

    personal_list = Personal.objects.all().annotate(
        monto_adeudado=Sum('salario') 
    )

    mantenimientos_list = Mantenimiento.objects.all().select_related('id_personal') 
    total_costo = mantenimientos_list.aggregate(Sum('costo'))['costo__sum'] or 0.00
    
    context = {
        'personal': personal_list,
        'mantenimientos': mantenimientos_list,
        'total_costo_mantenimiento': total_costo,
    }
    
    return render(request, 'financiera.html', context)



