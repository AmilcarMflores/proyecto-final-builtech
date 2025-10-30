from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import F, Q

TIPO_PERSONA_CHOICES = [
    ('propietario', 'Propietario'),
    ('inquilino', 'Inquilino'),
]

ESTADO_AREA_CHOICES = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo')
]

ESTADO_RESERVA_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('confirmada', 'Confirmada'),
    ('cancelada', 'Cancelada'),
]

ESTADO_FACTURA_CHOICES = [
    ('emitida', 'Emitida'),
    ('pagada', 'Pagada'),
    ('anulada', 'Anulada'),
    ('vencida', 'Vencida'),
]

TIPO_PAGO_CHOICES = [
    ('reserva', 'Reserva'),
    ('transferencia', 'Transferencia'),
    ('efectivo', 'Efectivo'),
    ('tarjeta', 'Tarjeta'),
]


class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)
    ci = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    correo = models.EmailField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_PERSONA_CHOICES)

    class Meta:
        db_table = 'persona'


    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.tipo})"
    
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, db_column='id_persona')
    nombre_usuario = models.CharField(max_length=150, unique=True)
    contrasena_hash = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, default='activo')
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return self.nombre_usuario

class AreaComun(models.Model):
    id_area = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_AREA_CHOICES)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'area_comun'

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario'
    )
    id_area = models.ForeignKey(
        AreaComun,
        on_delete=models.CASCADE,
        db_column='id_area'
    )
    fecha_res = models.DateField()
    hora_ini = models.TimeField()
    duracion = models.IntegerField(help_text="Duración en horas.")
    estado = models.CharField(max_length=20, choices=ESTADO_RESERVA_CHOICES, default='pendiente')
    numero_personas = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'reserva'
        unique_together = ('id_area', 'fecha_res', 'hora_ini') 

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.id_area.nombre} ({self.fecha_res})"



class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_emision = models.DateField(default=timezone.now) # Usamos default=timezone.now
    monto_total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_FACTURA_CHOICES)
    qr_code_url = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'factura'
        
    def __str__(self):
        return f'Factura #{self.pk} - {self.monto_total} ({self.get_estado_display()})'

class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_factura = models.ForeignKey(Factura, on_delete=models.CASCADE, db_column='id_factura') 
    id_reserva = models.ForeignKey(
        Reserva,
        on_delete=models.SET_NULL,
        db_column='id_reserva',
        null=True,
        blank=True
    )
    id_nomina = models.IntegerField(null=True, blank=True) 
    
    tipo = models.CharField(max_length=50, choices=TIPO_PAGO_CHOICES)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    referencia = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'pago'

    def __str__(self):
        return f"Pago {self.id_pago} - {self.tipo} - {self.monto}"


ROL_PERSONAL_CHOICES = [
    ('admin', 'Administrador'),
    ('recepcion', 'Recepción'),
    ('mantenimiento', 'Mantenimiento'),
    ('rrhh', 'Recursos Humanos'),
    ('contabilidad', 'Contabilidad'),
    ('seguridad', 'Seguridad'),
]

ESTADO_PERSONAL_CHOICES = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
]

class Personal(models.Model):
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
    rol = models.CharField(
        max_length=15, 
        choices=ROL_PERSONAL_CHOICES,
        default='mantenimiento'
    )
    
    estado = models.CharField(
        max_length=8, 
        choices=ESTADO_PERSONAL_CHOICES,
        default='activo'
    )
    telefono = models.CharField(max_length=15, null=True, blank=True)
    correo = models.EmailField(unique=True)
    fecha_contratacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.get_rol_display()})"
    
    class Meta:
        db_table = 'personal'
        verbose_name_plural = "Personal"
        managed = False


class Mantenimiento(models.Model):
    activo = models.ForeignKey(
        'Activo', 
        on_delete=models.PROTECT,
        related_name='registros_mantenimiento'
    )
    
    personal_asignado = models.ForeignKey(
        'Personal', 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='mantenimientos_realizados'
    )
    
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    descripcion_trabajo = models.TextField()
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    estado_mantenimiento = models.CharField(
        max_length=15, 
        choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En Proceso'), ('completado', 'Completado')],
        default='pendiente'
    )
    
    def __str__(self):
        return f"Mantenimiento de {self.activo.nombre} - {self.fecha_inicio.strftime('%Y-%m-%d')}"
    
    class Meta:
        db_table = 'mantenimiento'
        verbose_name_plural = "Mantenimientos"
        ordering = ['-fecha_inicio']
        managed = False

ESTADO_ACTIVO_CHOICES = [
    ('operativo', 'Operativo'),
    ('fuera_servicio', 'Fuera de Servicio'),
    ('baja', 'Dado de Baja'),
]

class Activo(models.Model):
    
    nombre = models.CharField(max_length=100) 
    tipo = models.CharField(max_length=50)   
    
    ubicacion = models.CharField(max_length=100, null=True, blank=True) 
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_ACTIVO_CHOICES,
        default='operativo'
    )
    
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'activo'
        managed = False