from django.db import models
from usuarios.models import Usuario
from rutas.models import Ruta

class Estudiante(models.Model):
    TIPO_DOCUMENTO = [
        ('TARJETA_IDENTIDAD',          'Tarjeta de Identidad'),
        ('CEDULA_CIUDADANIA',          'Cédula de Ciudadanía'),
        ('CEDULA_EXTRANJERIA',         'Cédula de Extranjería'),
        ('PASAPORTE',                  'Pasaporte'),
        ('REGISTRO_CIVIL',             'Registro Civil'),
        ('PERMISO_PROTECCION_TEMPORAL','Permiso de Protección Temporal'),
    ]
    TIPO_SANGRE = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('O+','O+'),('O-','O-'),('AB+','AB+'),('AB-','AB-'),
    ]

    documento        = models.CharField(max_length=20, primary_key=True)
    tipo_documento   = models.CharField(max_length=30, choices=TIPO_DOCUMENTO)
    nombre           = models.CharField(max_length=100)
    apellido         = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    direccion        = models.CharField(max_length=200, blank=True, null=True)
    telefono         = models.CharField(max_length=20,  blank=True, null=True)
    grado            = models.CharField(max_length=100, blank=True, null=True)
    institucion      = models.CharField(max_length=100, blank=True, null=True)

    # Información médica
    tipo_sangre          = models.CharField(max_length=5,  choices=TIPO_SANGRE, blank=True, null=True)
    enfermedades         = models.CharField(max_length=500, blank=True, null=True)
    alergias             = models.CharField(max_length=300, blank=True, null=True)
    medicamentos         = models.CharField(max_length=300, blank=True, null=True)
    observaciones_medicas= models.CharField(max_length=500, blank=True, null=True)

    # Contacto de emergencia
    contacto_emergencia_nombre    = models.CharField(max_length=100, blank=True, null=True)
    contacto_emergencia_telefono  = models.CharField(max_length=20,  blank=True, null=True)
    contacto_emergencia_parentesco= models.CharField(max_length=50,  blank=True, null=True)

    activo       = models.BooleanField(default=True)
    cedula_padre = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='cedula_padre'
    )
    codigo_ruta  = models.ForeignKey(
        Ruta,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='codigo_ruta'
    )
    fecha_registro      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'estudiante'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"