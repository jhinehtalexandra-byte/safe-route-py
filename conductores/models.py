# conductores/models.py

from django.db import models
from usuarios.models import Usuario


class Conductor(models.Model):
    CATEGORIA_LICENCIA = [
        ('B1', 'B1 — Automóviles'),
        ('B2', 'B2 — Camiones/buses pequeños'),
        ('B3', 'B3 — Articulados'),
        ('C1', 'C1 — Enseñanza automóvil'),
        ('C2', 'C2 — Enseñanza pesados'),
        ('C3', 'C3 — Enseñanza articulados'),
    ]
    TIPO_VEHICULO = [
        ('BUS',        'Bus'),
        ('BUSETA',     'Buseta'),
        ('MICROBUS',   'Microbús'),
        ('VAN',        'Van'),
        ('CAMPERO',    'Campero'),
        ('AUTOMOVIL',  'Automóvil'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='conductor_cedula',
        related_name='perfil_conductor',
        limit_choices_to={'rol': 'CONDUCTOR'},
    )

    # ── Licencia ──────────────────────────────────────────────
    numero_licencia       = models.CharField(max_length=30, blank=True, null=True, unique=True)
    categoria_licencia    = models.CharField(max_length=5,  choices=CATEGORIA_LICENCIA, blank=True, null=True)
    fecha_expedicion_lic  = models.DateField(blank=True, null=True)
    fecha_vencimiento_lic = models.DateField(blank=True, null=True)
    lugar_expedicion_lic  = models.CharField(max_length=100, blank=True, null=True)

    # ── Vehículo ──────────────────────────────────────────────
    placa              = models.CharField(max_length=10, blank=True, null=True)
    tipo_vehiculo      = models.CharField(max_length=20, choices=TIPO_VEHICULO, blank=True, null=True)
    marca_vehiculo     = models.CharField(max_length=50, blank=True, null=True)
    modelo_vehiculo    = models.CharField(max_length=50, blank=True, null=True)
    anio_vehiculo      = models.PositiveSmallIntegerField(blank=True, null=True)
    color_vehiculo     = models.CharField(max_length=30, blank=True, null=True)
    capacidad_pasajeros = models.PositiveSmallIntegerField(blank=True, null=True)

    # ── Documentos del vehículo ───────────────────────────────
    numero_soat            = models.CharField(max_length=30, blank=True, null=True)
    fecha_vencimiento_soat = models.DateField(blank=True, null=True)
    numero_tecnomecanica   = models.CharField(max_length=30, blank=True, null=True)
    fecha_vencimiento_tecno = models.DateField(blank=True, null=True)

    # ── Experiencia y notas ───────────────────────────────────
    anios_experiencia   = models.PositiveSmallIntegerField(default=0)
    observaciones       = models.TextField(blank=True, null=True)
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = 'conductor'
        verbose_name        = 'Conductor'
        verbose_name_plural = 'Conductores'

    def __str__(self):
        return self.usuario.nombre

    @property
    def licencia_vencida(self):
        from django.utils import timezone
        if self.fecha_vencimiento_lic:
            return self.fecha_vencimiento_lic < timezone.now().date()
        return False

    @property
    def soat_vencido(self):
        from django.utils import timezone
        if self.fecha_vencimiento_soat:
            return self.fecha_vencimiento_soat < timezone.now().date()
        return False

    @property
    def tecno_vencida(self):
        from django.utils import timezone
        if self.fecha_vencimiento_tecno:
            return self.fecha_vencimiento_tecno < timezone.now().date()
        return False