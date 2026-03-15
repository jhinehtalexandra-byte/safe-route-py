from django.db import models

class Usuario(models.Model):
    TIPO_DOCUMENTO = [
        ('CEDULA_CIUDADANIA',          'Cédula de Ciudadanía'),
        ('CEDULA_EXTRANJERIA',         'Cédula de Extranjería'),
        ('PASAPORTE',                  'Pasaporte'),
        ('TARJETA_IDENTIDAD',          'Tarjeta de Identidad'),
        ('PERMISO_PROTECCION_TEMPORAL','Permiso de Protección Temporal'),
    ]
    ROL = [
        ('ADMIN',     'Administrador'),
        ('CONDUCTOR', 'Conductor'),
        ('PADRE',     'Padre'),
    ]

    cedula           = models.CharField(max_length=20, primary_key=True)
    tipo_documento   = models.CharField(max_length=30, choices=TIPO_DOCUMENTO)
    user_name        = models.CharField(max_length=50, unique=True)
    password         = models.CharField(max_length=255)
    nombre           = models.CharField(max_length=100)
    email            = models.EmailField(max_length=100, unique=True)
    telefono         = models.CharField(max_length=20, blank=True, null=True)
    rol              = models.CharField(max_length=20, choices=ROL)
    activo           = models.BooleanField(default=True)
    fecha_creacion   = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuario'   # ← nombre exacto de tu tabla en PostgreSQL

    def __str__(self):
        return f"{self.nombre} ({self.rol})"
