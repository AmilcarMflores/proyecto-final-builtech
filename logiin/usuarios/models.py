from django.db import models
from django.contrib.auth.models import User

class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True, db_column='id_persona')
    ci = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('propietario', 'Propietario'),
            ('inquilino', 'Inquilino')
        ]
    )

    class Meta:
        db_table = 'persona'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.tipo})"


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, db_column='id_usuario')
    id_persona = models.ForeignKey(Persona, on_delete=models.CASCADE, db_column='id_persona')
    nombre_usuario = models.CharField(max_length=150, unique=True)
    contrasena_hash = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, default='activo')

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.nombre_usuario
