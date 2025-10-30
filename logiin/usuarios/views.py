# usuarios/views.py
import os, json
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from datetime import datetime, timedelta

# Rutas a ficheros JSON
DATA_DIR = os.path.join(settings.BASE_DIR, 'usuarios', 'data')
USUARIOS_FILE = os.path.join(DATA_DIR, 'usuarios.json')
RESIDENTES_FILE = os.path.join(DATA_DIR, 'residentes.json')
PERSONAL_FILE = os.path.join(DATA_DIR, 'personal.json')
APARTAMENTOS_FILE = os.path.join(DATA_DIR, 'apartamentos.json')

# --- Helpers para JSON ---------------------------------------------------
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path):
    ensure_data_dir()
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(path, data):
    ensure_data_dir()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- Gestión de intentos fallidos (seguridad) ----------------------------
def get_intentos_fallidos(request):
    return request.session.get('login_intentos', 0)

def set_intentos_fallidos(request, intentos):
    request.session['login_intentos'] = intentos

def get_ultimo_intento(request):
    ts = request.session.get('ultimo_intento')
    return datetime.fromisoformat(ts) if ts else None

def set_ultimo_intento(request):
    request.session['ultimo_intento'] = datetime.now().isoformat()

def esta_bloqueado(request):
    intentos = get_intentos_fallidos(request)
    if intentos < 3:
        return False
    ultimo = get_ultimo_intento(request)
    if ultimo and (datetime.now() - ultimo) < timedelta(minutes=5):
        return True
    # Resetear si pasaron 5 minutos
    set_intentos_fallidos(request, 0)
    return False

# --- Home / Auth (admin-register/login) ---------------------------------
def home(request):
    return render(request, 'usuarios/home.html')

def registro_admin(request):
    usuarios = load_json(USUARIOS_FILE)
    if any(u.get('rol') == 'administrador' for u in usuarios):
        messages.info(request, "Ya existe un administrador. Inicia sesión.")
        return redirect('login')

    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        password = request.POST.get('password', '')
        nombre = request.POST.get('nombre', '')
        correo = request.POST.get('correo', '')
        telefono = request.POST.get('telefono', '')

        # === Validación de contraseña fuerte ===
        if len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return redirect('registro')
        if not any(c.isupper() for c in password):
            messages.error(request, "La contraseña debe contener al menos una letra mayúscula.")
            return redirect('registro')
        if not any(c.isdigit() for c in password):
            messages.error(request, "La contraseña debe contener al menos un número.")
            return redirect('registro')
        # ======================================

        nuevo = {
            "usuario": usuario,
            "password": password,
            "rol": "administrador",
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "must_change_password": password == "BuildTech"
        }
        usuarios.append(nuevo)
        save_json(USUARIOS_FILE, usuarios)
        messages.success(request, "Administrador registrado correctamente.")
        return redirect('login')

    return render(request, 'usuarios/registro.html')

def login_view(request):
    if request.method == 'POST':
        # Verificar bloqueo
        if esta_bloqueado(request):
            messages.error(request, "Demasiados intentos fallidos. Espera 5 minutos.")
            return render(request, 'usuarios/login.html')

        usuario = request.POST.get('usuario')
        password = request.POST.get('password')
        not_bot = request.POST.get('not_bot')

        if not not_bot:
            messages.error(request, "Confirma que no eres un robot.")
            return redirect('login')

        usuarios = load_json(USUARIOS_FILE)
        user = next((u for u in usuarios if u['usuario'] == usuario and u['password'] == password), None)
        if not user:
            # Registrar intento fallido
            intentos = get_intentos_fallidos(request) + 1
            set_intentos_fallidos(request, intentos)
            set_ultimo_intento(request)
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')

        # Éxito: resetear intentos
        request.session['login_intentos'] = 0
        request.session['usuario'] = user['usuario']
        request.session['rol'] = user['rol']

        if user.get('must_change_password'):
            return redirect('cambiar_password')

        if user['rol'] == 'administrador':
            return redirect('dashboard_admin')
        else:
            return redirect('dashboard_residente')

    # GET
    if esta_bloqueado(request):
        messages.error(request, "Demasiados intentos fallidos. Espera 5 minutos.")
    return render(request, 'usuarios/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

# --- Cambio de contraseña ------------------------------------------------
def cambiar_password(request):
    usuario_actual = request.session.get('usuario')
    if not usuario_actual:
        return redirect('login')
    usuarios = load_json(USUARIOS_FILE)
    user = next((u for u in usuarios if u['usuario'] == usuario_actual), None)
    if not user:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    if request.method == 'POST':
        nueva = request.POST.get('nueva_password')
        if not nueva or len(nueva) < 8:
            messages.error(request, "La contraseña debe tener mínimo 8 caracteres.")
            return redirect('cambiar_password')
        for u in usuarios:
            if u['usuario'] == usuario_actual:
                u['password'] = nueva
                u['must_change_password'] = False
        save_json(USUARIOS_FILE, usuarios)
        messages.success(request, "Contraseña actualizada. Por favor inicia sesión de nuevo.")
        request.session.flush()
        return redirect('login')

    return render(request, 'usuarios/cambiar_password.html', {"usuario": usuario_actual})

# --- DASHBOARDS ----------------------------------------------------------
def dashboard_admin(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    residentes = load_json(RESIDENTES_FILE)
    personal = load_json(PERSONAL_FILE)
    apartamentos = load_json(APARTAMENTOS_FILE)
    return render(request, 'usuarios/dashboard_admin.html', {
        "residentes": residentes,
        "personal": personal,
        "apartamentos": apartamentos,
        "usuario_actual": request.session.get("usuario")
    })

def dashboard_residente(request):
    if request.session.get('rol') != 'residente':
        return redirect('login')

    usuario_actual = request.session.get('usuario')
    residentes = load_json(RESIDENTES_FILE)
    user = next((r for r in residentes if r.get("usuario") == usuario_actual), None)
    if not user:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    # Cargar datos adicionales
    pagos = load_json(os.path.join(DATA_DIR, 'pagos.json'))
    reservas = load_json(os.path.join(DATA_DIR, 'reservas.json'))
    notificaciones = load_json(os.path.join(DATA_DIR, 'notificaciones.json'))

    # Filtrar por usuario
    pagos_usuario = [p for p in pagos if p.get('usuario') == usuario_actual]
    reservas_usuario = [r for r in reservas if r.get('usuario') == usuario_actual]
    notificaciones_usuario = [n for n in notificaciones if n.get('usuario') == usuario_actual]

    # Ordenar y limitar
    pagos_recientes = sorted(pagos_usuario, key=lambda x: x.get('fecha', ''), reverse=True)[:3]
    reservas_proximas = sorted(reservas_usuario, key=lambda x: x.get('fecha', ''))[:3]
    notificaciones_pendientes = [n for n in notificaciones_usuario if not n.get('leida', False)][:3]

    context = {
        "user": user,
        "pagos_recientes": pagos_recientes,
        "reservas_proximas": reservas_proximas,
        "notificaciones_pendientes": notificaciones_pendientes,
        "total_notificaciones": len(notificaciones_pendientes)
    }

    return render(request, 'usuarios/dashboard_residente.html', context)

# --- RESIDENTES ----------------------------------------------------------
def gestion_residentes(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    residentes = load_json(RESIDENTES_FILE)
    return render(request, 'usuarios/gestion_residentes.html', {"residentes": residentes})

def agregar_residente_from_admin(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')

    if request.method == 'POST':
        usuarios = load_json(USUARIOS_FILE)
        residentes = load_json(RESIDENTES_FILE)

        usuario = request.POST.get('usuario')
        password = request.POST.get('password')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        ci = request.POST.get('ci')
        telefono = request.POST.get('telefono')
        correo = request.POST.get('correo')
        departamento = request.POST.get('departamento')

        nuevo = {
            "usuario": usuario,
            "password": password,
            "rol": "residente",
            "nombre": nombre,
            "apellido": apellido,
            "ci": ci,
            "telefono": telefono,
            "correo": correo,
            "departamento": departamento
        }
        residentes.append(nuevo)
        save_json(RESIDENTES_FILE, residentes)

        usuarios.append({
            "usuario": usuario,
            "password": password,
            "rol": "residente",
            "nombre": f"{nombre} {apellido}",
            "correo": correo,
            "must_change_password": password == "BuildTech"
        })
        save_json(USUARIOS_FILE, usuarios)
        messages.success(request, "Residente agregado correctamente.")
        return redirect('dashboard_admin')

    apartamentos = load_json(APARTAMENTOS_FILE)
    return render(request, 'usuarios/agregar_residente.html', {"apartamentos": apartamentos})

def editar_residente(request, usuario):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    residentes = load_json(RESIDENTES_FILE)
    r = next((x for x in residentes if x.get('usuario') == usuario), None)
    if not r:
        messages.error(request, "Residente no encontrado.")
        return redirect('gestion_residentes')
    if request.method == 'POST':
        r['nombre'] = request.POST.get('nombre')
        r['apellido'] = request.POST.get('apellido')
        r['telefono'] = request.POST.get('telefono')
        r['correo'] = request.POST.get('correo')
        r['departamento'] = request.POST.get('departamento')
        save_json(RESIDENTES_FILE, residentes)
        messages.success(request, "Residente actualizado.")
        return redirect('gestion_residentes')
    apartamentos = load_json(APARTAMENTOS_FILE)
    return render(request, 'usuarios/editar_residente.html', {"residente": r, "apartamentos": apartamentos})

def borrar_residente(request, usuario):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    residentes = load_json(RESIDENTES_FILE)
    residentes = [r for r in residentes if r.get('usuario') != usuario]
    save_json(RESIDENTES_FILE, residentes)

    usuarios = load_json(USUARIOS_FILE)
    usuarios = [u for u in usuarios if u.get('usuario') != usuario]
    save_json(USUARIOS_FILE, usuarios)
    messages.success(request, "Residente eliminado.")
    return redirect('gestion_residentes')

def cambiar_password_residente(request):
    if request.session.get('rol') != 'residente':
        return redirect('login')

    usuario_actual = request.session.get('usuario')
    if not usuario_actual:
        return redirect('login')

    usuarios = load_json(USUARIOS_FILE)
    user = next((u for u in usuarios if u['usuario'] == usuario_actual), None)
    if not user:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    if request.method == 'POST':
        nueva = request.POST.get('nueva_password')
        if not nueva or len(nueva) < 8:
            messages.error(request, "La contraseña debe tener mínimo 8 caracteres.")
            return redirect('cambiar_password_residente')

        for u in usuarios:
            if u['usuario'] == usuario_actual:
                u['password'] = nueva
                u['must_change_password'] = False
        save_json(USUARIOS_FILE, usuarios)

        residentes = load_json(RESIDENTES_FILE)
        for r in residentes:
            if r['usuario'] == usuario_actual:
                r['password'] = nueva
        save_json(RESIDENTES_FILE, residentes)

        messages.success(request, "Contraseña actualizada correctamente.")
        return redirect('dashboard_residente')

    return render(request, 'usuarios/cambiar_password_residente.html', {"usuario": usuario_actual})

# --- PERSONAL ------------------------------------------------------------
def gestion_personal(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    personal = load_json(PERSONAL_FILE)
    return render(request, 'usuarios/personal.html', {"personal": personal})

def agregar_personal(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    personal = load_json(PERSONAL_FILE)
    if request.method == 'POST':
        nuevo = {
            "id": (max([p.get('id', 0) for p in personal]) + 1) if personal else 1,
            "nombre": request.POST.get('nombre') or "",
            "ci": request.POST.get('ci') or "",
            "telefono": request.POST.get('telefono') or "",
            "cargo": request.POST.get('cargo') or "",
            "usuario": request.POST.get('usuario') or "",
            "estado": "activo"
        }
        personal.append(nuevo)
        save_json(PERSONAL_FILE, personal)
        messages.success(request, "Personal añadido correctamente.")
        return redirect('gestion_personal')
    return render(request, 'usuarios/agregar_personal.html')

def agregar_personal_provisional(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    personal = load_json(PERSONAL_FILE)
    if request.method == 'POST':
        nuevo = {
            "id": (max([p.get('id', 0) for p in personal]) + 1) if personal else 1,
            "nombre": request.POST.get('nombre') or "",
            "cargo": request.POST.get('cargo') or "",
            "telefono": request.POST.get('telefono') or "",
            "usuario": request.POST.get('usuario') or "",
            "estado": "provisional"
        }
        personal.append(nuevo)
        save_json(PERSONAL_FILE, personal)
        messages.success(request, "Personal provisional añadido correctamente.")
        return redirect('gestion_personal')
    return render(request, 'usuarios/agregar_personal_provisional.html')

def editar_personal(request, pid):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    personal = load_json(PERSONAL_FILE)
    p = next((x for x in personal if x['id'] == int(pid)), None)
    if not p:
        messages.error(request, "Registro no encontrado.")
        return redirect('gestion_personal')
    if request.method == 'POST':
        p['nombre'] = request.POST.get('nombre')
        p['cargo'] = request.POST.get('cargo')
        p['telefono'] = request.POST.get('telefono')
        p['correo'] = request.POST.get('correo')
        save_json(PERSONAL_FILE, personal)
        messages.success(request, "Personal actualizado.")
        return redirect('gestion_personal')
    return render(request, 'usuarios/editar_personal.html', {"p": p})

def borrar_personal(request, pid):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    
    try:
        pid = int(pid)
    except (ValueError, TypeError):
        messages.error(request, "ID de personal inválido.")
        return redirect('gestion_personal')

    personal = load_json(PERSONAL_FILE)
    if not any(p.get('id') == pid for p in personal):
        messages.warning(request, "El registro de personal no existe.")
        return redirect('gestion_personal')

    personal = [p for p in personal if p.get('id') != pid]
    save_json(PERSONAL_FILE, personal)
    messages.success(request, "Personal eliminado correctamente.")
    return redirect('gestion_personal')

# --- APARTAMENTOS --------------------------------------------------------
def gestion_apartamentos(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    apartamentos = load_json(APARTAMENTOS_FILE)
    return render(request, 'usuarios/gestion_apartamentos.html', {"apartamentos": apartamentos})

def agregar_apartamento(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    apartamentos = load_json(APARTAMENTOS_FILE)
    if request.method == 'POST':
        try:
            nuevo_id = max([a.get('id', 0) for a in apartamentos]) + 1 if apartamentos else 1
        except:
            nuevo_id = len(apartamentos) + 1
        nuevo = {
            "id": int(nuevo_id),
            "piso": int(request.POST.get('piso') or 0),
            "puerta": request.POST.get('puerta') or "",
            "capacidad": int(request.POST.get('capacidad') or 1),
            "tipo": request.POST.get('tipo') or "",
            "descripcion": request.POST.get('descripcion') or "",
            "estado": request.POST.get('estado') or "disponible",
            "propietario": None
        }
        apartamentos.append(nuevo)
        save_json(APARTAMENTOS_FILE, apartamentos)
        messages.success(request, "Apartamento añadido correctamente.")
        return redirect('gestion_apartamentos')
    return render(request, 'usuarios/agregar_apartamento.html')

def editar_apartamento(request, apt_id):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    apartamentos = load_json(APARTAMENTOS_FILE)
    apt = next((a for a in apartamentos if a.get('id') == int(apt_id)), None)
    if not apt:
        messages.error(request, "Apartamento no encontrado.")
        return redirect('gestion_apartamentos')
    if request.method == 'POST':
        apt['piso'] = int(request.POST.get('piso') or apt.get('piso', 0))
        apt['puerta'] = request.POST.get('puerta') or apt.get('puerta', '')
        apt['capacidad'] = int(request.POST.get('capacidad') or apt.get('capacidad', 1))
        apt['tipo'] = request.POST.get('tipo') or apt.get('tipo', '')
        apt['descripcion'] = request.POST.get('descripcion') or apt.get('descripcion', '')
        apt['estado'] = request.POST.get('estado') or apt.get('estado', 'disponible')
        save_json(APARTAMENTOS_FILE, apartamentos)
        messages.success(request, "Apartamento actualizado correctamente.")
        return redirect('gestion_apartamentos')
    return render(request, 'usuarios/editar_apartamento.html', {"apt": apt})

def eliminar_apartamento(request, apt_id):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    apartamentos = load_json(APARTAMENTOS_FILE)
    apartamentos = [a for a in apartamentos if a.get('id') != int(apt_id)]
    save_json(APARTAMENTOS_FILE, apartamentos)
    messages.success(request, "Apartamento eliminado correctamente.")
    return redirect('gestion_apartamentos')

def anadir_residente_departamento(request, numero):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    apartamentos = load_json(APARTAMENTOS_FILE)
    residentes = load_json(RESIDENTES_FILE)
    usuarios = load_json(USUARIOS_FILE)
    apt = next((a for a in apartamentos if int(a.get('id', -1)) == int(numero)), None)
    if not apt:
        messages.error(request, "Apartamento no encontrado.")
        return redirect('gestion_apartamentos')
    if apt.get('estado') != 'disponible':
        messages.error(request, "El apartamento no está disponible para agregar residentes.")
        return redirect('gestion_apartamentos')
    if request.method == 'POST':
        usuario = (request.POST.get('usuario') or '').strip()
        password = (request.POST.get('password') or '').strip()
        nombre = (request.POST.get('nombre') or '').strip()
        apellido = (request.POST.get('apellido') or '').strip()
        ci = (request.POST.get('ci') or '').strip()
        telefono = (request.POST.get('telefono') or '').strip()
        correo = (request.POST.get('correo') or '').strip()
        if not usuario or not password:
            messages.error(request, "Usuario y contraseña son obligatorios.")
            return redirect('anadir_residente_departamento', numero=numero)
        if any(u.get('usuario') == usuario for u in usuarios):
            messages.error(request, "Ya existe ese usuario. Elige otro nombre de usuario.")
            return redirect('anadir_residente_departamento', numero=numero)
        if ci and any(r.get('ci') == ci for r in residentes):
            messages.error(request, "Ya existe un residente con ese CI.")
            return redirect('anadir_residente_departamento', numero=numero)
        nuevo_res = {
            "usuario": usuario,
            "password": password,
            "rol": "residente",
            "nombre": nombre,
            "apellido": apellido,
            "ci": ci,
            "telefono": telefono,
            "correo": correo,
            "departamento": int(numero)
        }
        residentes.append(nuevo_res)
        save_json(RESIDENTES_FILE, residentes)
        usuarios.append({
            "usuario": usuario,
            "password": password,
            "rol": "residente",
            "nombre": f"{nombre} {apellido}".strip(),
            "correo": correo,
            "must_change_password": password == "BuildTech"
        })
        save_json(USUARIOS_FILE, usuarios)
        try:
            capacidad = int(apt.get('capacidad', 1))
        except:
            capacidad = 1
        ocupantes = len([r for r in residentes if int(r.get('departamento', -1)) == int(numero)])
        if ocupantes >= capacidad:
            apt['estado'] = 'ocupado'
        else:
            apt['estado'] = 'disponible'
        apt['propietario'] = f"{nombre} {apellido}".strip()
        save_json(APARTAMENTOS_FILE, apartamentos)
        messages.success(request, "Residente agregado correctamente al apartamento.")
        return redirect('gestion_apartamentos')
    return render(request, 'usuarios/agregar_residente.html', {"apartamento": apt, "numero": numero})

# --- FINANZAS E INFORMES -------------------------------------------------
def gestion_finanzas(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    return render(request, 'usuarios/finanzas.html')

def panel_informes(request):
    if request.session.get('rol') != 'administrador':
        return redirect('login')
    return render(request, 'usuarios/informes.html')

# --- RESERVAS Y PAGOS PARA RESIDENTES ------------------------------------
def reservas_residente(request):
    if request.session.get('rol') != 'residente':
        return redirect('login')
    return render(request, 'usuarios/reservas_residente.html', {
        "usuario": request.session.get("usuario")
    })

def pagos_residente(request):
    if request.session.get('rol') != 'residente':
        return redirect('login')
    return render(request, 'usuarios/pagos_residente.html', {
        "usuario": request.session.get("usuario")
    })