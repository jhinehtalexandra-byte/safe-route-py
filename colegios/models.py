from django.db import models
from cloudinary.models import CloudinaryField
from usuarios.models import Usuario


class Colegio(models.Model):
    TIPO_INSTITUCION = [
        ('PUBLICA',   'Pública'),
        ('PRIVADA',   'Privada'),
        ('CONCESION', 'Concesión'),
        ('TECNICA',   'Técnica'),
    ]
    PLAN = [
        ('BASICO',    'Básico'),
        ('ESTANDAR',  'Estándar'),
        ('PREMIUM',   'Premium'),
        ('ILIMITADO', 'Ilimitado'),
    ]

    nit                  = models.CharField(max_length=20, primary_key=True)
    nombre_institucion   = models.CharField(max_length=200)
    tipo_institucion     = models.CharField(max_length=20, choices=TIPO_INSTITUCION)
    codigo_dane          = models.CharField(max_length=20, blank=True, null=True)
    direccion            = models.CharField(max_length=300)
    ciudad               = models.CharField(max_length=100)
    departamento         = models.CharField(max_length=100, blank=True, null=True)
    telefono             = models.CharField(max_length=20)
    email_institucional  = models.EmailField(max_length=200, unique=True)
    sitio_web            = models.URLField(max_length=200, blank=True, null=True)
    nombre_rector        = models.CharField(max_length=200)
    telefono_rector      = models.CharField(max_length=20, blank=True, null=True)
    email_rector         = models.EmailField(max_length=200, blank=True, null=True)
    max_rutas            = models.IntegerField(default=10)
    max_conductores      = models.IntegerField(default=20)
    max_estudiantes      = models.IntegerField(default=500)
    plan                 = models.CharField(max_length=20, choices=PLAN, default='BASICO')
    observaciones        = models.TextField(max_length=500, blank=True, null=True)
    activo               = models.BooleanField(default=True)
    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion  = models.DateTimeField(auto_now=True)

    # Logo del colegio almacenado en Cloudinary
    logo = CloudinaryField(
        'logo',
        folder='logos_colegios',
        blank=True,
        null=True,
    )

    # Relación con el usuario de acceso al sistema
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='colegio_perfil'
    )

    class Meta:
        db_table = 'colegio'
        ordering = ['nombre_institucion']

    def __str__(self):
        return f"{self.nombre_institucion} ({self.nit})"