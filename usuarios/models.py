# usuarios/models.py
import re
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from cloudinary.models import CloudinaryField


class Usuario(models.Model):
    TIPO_DOCUMENTO = [
        ('CEDULA_CIUDADANIA',           'Cédula de Ciudadanía'),
        ('CEDULA_EXTRANJERIA',          'Cédula de Extranjería'),
        ('PASAPORTE',                   'Pasaporte'),
        ('TARJETA_IDENTIDAD',           'Tarjeta de Identidad'),
        ('PERMISO_PROTECCION_TEMPORAL', 'Permiso de Protección Temporal'),
        ('NIT',                         'NIT'),
    ]
    ROL = [
        ('ADMIN',     'Administrador'),
        ('COLEGIO',   'Colegio / Institución'),
        ('CONDUCTOR', 'Conductor'),
        ('MONITORA',  'Monitora'),
        ('PADRE',     'Padre'),
    ]

    cedula              = models.CharField(max_length=20, primary_key=True)
    tipo_documento      = models.CharField(max_length=30, choices=TIPO_DOCUMENTO)
    user_name           = models.CharField(max_length=50, unique=True)
    password            = models.CharField(max_length=255)         # siempre hasheado
    nombre              = models.CharField(max_length=100)
    email               = models.EmailField(max_length=100, unique=True)
    telefono            = models.CharField(max_length=20, blank=True, null=True)
    foto                = CloudinaryField(
        'foto',
        blank=True,
        null=True,
        folder='fotos_perfil',
    )
    rol                 = models.CharField(max_length=20, choices=ROL)
    activo              = models.BooleanField(default=True)
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

    # ── Helpers de contraseña ──────────────────────────────────────
    def set_password(self, raw_password):
        """Llama esto al crear o cambiar contraseña — NUNCA guardes texto plano."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Retorna True si la contraseña es correcta."""
        return check_password(raw_password, self.password)

    # ── Helpers de rol (útiles en las vistas y templates) ─────────
    @property
    def es_admin(self):
        return self.rol == 'ADMIN'

    @property
    def es_conductor(self):
        return self.rol == 'CONDUCTOR'

    @property
    def es_monitora(self):
        return self.rol == 'MONITORA'

    @property
    def es_padre(self):
        return self.rol == 'PADRE'

    @property
    def es_colegio(self):
        return self.rol == 'COLEGIO'


class Novedad(models.Model):
    TIPO = [
        ('RETRASO',        'Retraso en la ruta'),
        ('AUSENCIA_EST',   'Ausencia de estudiante'),
        ('FALLA_MECANICA', 'Falla mecánica del vehículo'),
        ('ACCIDENTE',      'Accidente de tránsito'),
        ('CLIMA',          'Condiciones climáticas'),
        ('OTRO',           'Otro'),
    ]
    ESTADO = [
        ('ACTIVA',   'Activa'),
        ('RESUELTA', 'Resuelta'),
    ]

    tipo        = models.CharField(max_length=20, choices=TIPO)
    descripcion = models.TextField()
    estado      = models.CharField(max_length=10, choices=ESTADO, default='ACTIVA')
    fecha_hora  = models.DateTimeField(auto_now_add=True)

    conductor   = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='novedades_registradas',
        limit_choices_to={'rol': 'CONDUCTOR'},
    )
    ruta        = models.ForeignKey(
        'rutas.Ruta',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='novedades',
    )
    estudiante  = models.ForeignKey(
        'estudiantes.Estudiante',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='novedades',
    )

    class Meta:
        db_table = 'novedad'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"


class AusenciaEstudiante(models.Model):
    ESTADO = [
        ('PENDIENTE',  'Pendiente de confirmar'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA',  'Cancelada'),
    ]

    estudiante   = models.ForeignKey(
        'estudiantes.Estudiante',
        on_delete=models.CASCADE,
        related_name='ausencias',
    )
    padre        = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='ausencias_reportadas',
        limit_choices_to={'rol': 'PADRE'},
    )
    fecha        = models.DateField()
    razon        = models.CharField(max_length=300, blank=True, null=True)
    estado       = models.CharField(max_length=12, choices=ESTADO, default='PENDIENTE')
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table        = 'ausencia_estudiante'
        ordering        = ['-fecha_reporte']
        unique_together = ('estudiante', 'fecha')

    def __str__(self):
        return f"Ausencia {self.estudiante} — {self.fecha}"