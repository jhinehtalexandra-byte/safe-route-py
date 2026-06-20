# monitoras/models.py
from django.db import models
from usuarios.models import Usuario


class Monitora(models.Model):
    NIVEL_EDUCATIVO = [
        ('BACHILLERATO', 'Bachillerato'),
        ('TECNICO',      'Técnico'),
        ('TECNOLOGO',    'Tecnólogo'),
        ('PROFESIONAL',  'Profesional'),
        ('POSGRADO',     'Posgrado'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='monitora_cedula',
        related_name='perfil_monitora',
        limit_choices_to={'rol': 'MONITORA'},
    )

    tiene_certificado_pa     = models.BooleanField(default=False)
    entidad_certificadora_pa = models.CharField(max_length=150, blank=True, null=True)
    fecha_certificado_pa     = models.DateField(blank=True, null=True)
    fecha_vencimiento_pa     = models.DateField(blank=True, null=True)

    nivel_educativo   = models.CharField(max_length=20, choices=NIVEL_EDUCATIVO, blank=True, null=True)
    anios_experiencia = models.PositiveSmallIntegerField(default=0)

    # ── CLAVE: db_column debe coincidir EXACTAMENTE con la columna en BD ──
    ruta_asignada = models.ForeignKey(
        'rutas.Ruta',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='monitoras',
        db_column='ruta_asignada',   # BD tiene 'ruta_asignada', no 'ruta_asignada_id'
    )

    observaciones       = models.TextField(blank=True, null=True)
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'monitora'
        managed   = True   # Django gestiona la tabla
        verbose_name        = 'Monitora'
        verbose_name_plural = 'Monitoras'

    def __str__(self):
        return self.usuario.nombre

    @property
    def certificado_vencido(self):
        from django.utils import timezone
        if self.tiene_certificado_pa and self.fecha_vencimiento_pa:
            return self.fecha_vencimiento_pa < timezone.now().date()
        return False

    @property
    def certificado_vigente(self):
        return self.tiene_certificado_pa and not self.certificado_vencido