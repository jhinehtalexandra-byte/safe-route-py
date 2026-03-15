from django.db import models
from usuarios.models import Usuario

class Ruta(models.Model):
    TURNO = [
        ('MAÑANA', 'Mañana'),
        ('TARDE',  'Tarde'),
        ('NOCHE',  'Noche'),
    ]

    codigo           = models.CharField(max_length=50, primary_key=True)
    nombre           = models.CharField(max_length=100)
    descripcion      = models.CharField(max_length=500, blank=True, null=True)
    hora_inicio      = models.TimeField(blank=True, null=True)
    hora_fin         = models.TimeField(blank=True, null=True)
    turno            = models.CharField(max_length=20, choices=TURNO, blank=True, null=True)
    capacidad_maxima = models.IntegerField(blank=True, null=True)
    activo           = models.BooleanField(default=True)
    conductor_cedula = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='conductor_cedula'
    )
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ruta'

    def __str__(self):
        return self.nombre