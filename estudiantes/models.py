# estudiantes/models.py
from django.db import models
from usuarios.models import Usuario
from rutas.models import Ruta


class Acudiente(models.Model):
    TIPO_DOCUMENTO = [
        ('CEDULA_CIUDADANIA',           'Cédula de Ciudadanía'),
        ('CEDULA_EXTRANJERIA',          'Cédula de Extranjería'),
        ('PASAPORTE',                   'Pasaporte'),
        ('TARJETA_IDENTIDAD',           'Tarjeta de Identidad'),
        ('PERMISO_PROTECCION_TEMPORAL', 'Permiso de Protección Temporal'),
    ]
    TIPO_NOTIFICACIONES = [
        ('TODAS',    'Todas — recogida, llegada, entrega, pagos, ausencias'),
        ('CRITICAS', 'Solo críticas — incidentes, autorizaciones médicas'),
    ]

    documento      = models.CharField(max_length=20, primary_key=True)
    tipo_documento = models.CharField(max_length=30, choices=TIPO_DOCUMENTO)
    nombre         = models.CharField(max_length=150)
    email          = models.EmailField(max_length=150, unique=True)
    telefono       = models.CharField(max_length=20, blank=True, null=True)

    activo           = models.BooleanField(default=True)
    token_invitacion = models.CharField(max_length=200, blank=True, null=True)
    cuenta_activada  = models.BooleanField(default=False)

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='acudiente_perfil',
        db_column='usuario_cedula',
    )

    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'acudiente'

    def __str__(self):
        return f"{self.nombre} ({self.documento})"


class Estudiante(models.Model):
    TIPO_DOCUMENTO = [
        ('TARJETA_IDENTIDAD',           'Tarjeta de Identidad'),
        ('CEDULA_CIUDADANIA',           'Cédula de Ciudadanía'),
        ('CEDULA_EXTRANJERIA',          'Cédula de Extranjería'),
        ('PASAPORTE',                   'Pasaporte'),
        ('REGISTRO_CIVIL',              'Registro Civil'),
        ('PERMISO_PROTECCION_TEMPORAL', 'Permiso de Protección Temporal'),
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

    LOCALIDAD = [
        ('USAQUEN',        'Usaquén'),
        ('CHAPINERO',      'Chapinero'),
        ('SANTA_FE',       'Santa Fe'),
        ('SAN_CRISTOBAL',  'San Cristóbal'),
        ('USME',           'Usme'),
        ('TUNJUELITO',     'Tunjuelito'),
        ('BOSA',           'Bosa'),
        ('KENNEDY',        'Kennedy'),
        ('FONTIBON',       'Fontibón'),
        ('ENGATIVA',       'Engativá'),
        ('SUBA',           'Suba'),
        ('BARRIOS_UNIDOS', 'Barrios Unidos'),
        ('TEUSAQUILLO',    'Teusaquillo'),
        ('MARTIRES',       'Los Mártires'),
        ('ANTONIO_NARINO', 'Antonio Nariño'),
        ('PUENTE_ARANDA',  'Puente Aranda'),
        ('CANDELARIA',     'La Candelaria'),
        ('RAFAEL_URIBE',   'Rafael Uribe Uribe'),
        ('CIUDAD_BOLIVAR', 'Ciudad Bolívar'),
        ('SUMAPAZ',        'Sumapaz'),
    ]

    localidad = models.CharField(
        max_length=30, choices=LOCALIDAD, blank=True, null=True
    )
    telefono         = models.CharField(max_length=20,  blank=True, null=True)
    grado            = models.CharField(max_length=100, blank=True, null=True)
    institucion      = models.CharField(max_length=100, blank=True, null=True)

    tipo_sangre           = models.CharField(max_length=5,   choices=TIPO_SANGRE, blank=True, null=True)
    enfermedades          = models.CharField(max_length=500, blank=True, null=True)
    alergias              = models.CharField(max_length=300, blank=True, null=True)
    medicamentos          = models.CharField(max_length=300, blank=True, null=True)
    observaciones_medicas = models.CharField(max_length=500, blank=True, null=True)

    contacto_emergencia_nombre     = models.CharField(max_length=100, blank=True, null=True)
    contacto_emergencia_telefono   = models.CharField(max_length=20,  blank=True, null=True)
    contacto_emergencia_parentesco = models.CharField(max_length=50,  blank=True, null=True)

    activo = models.BooleanField(default=True)

    codigo_ruta = models.ForeignKey(
        Ruta,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='codigo_ruta',
    )

    acudientes = models.ManyToManyField(
        Acudiente,
        through='EstudianteAcudiente',
        related_name='estudiantes',
        blank=True,
    )

    cedula_padre = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='cedula_padre',
    )

    fecha_registro      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'estudiante'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class EstudianteAcudiente(models.Model):
    TIPO_NOTIFICACIONES = [
        ('TODAS',    'Todas'),
        ('CRITICAS', 'Solo críticas'),
    ]

    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        db_column='estudiante',
    )
    acudiente = models.ForeignKey(
        Acudiente,
        on_delete=models.CASCADE,
        db_column='acudiente',
    )
    es_principal        = models.BooleanField(default=False)
    tipo_notificaciones = models.CharField(
        max_length=10,
        choices=TIPO_NOTIFICACIONES,
        default='TODAS',
    )
    fecha_vinculacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'estudiante_acudiente'
        unique_together = ('estudiante', 'acudiente')

    def __str__(self):
        rol = 'Principal' if self.es_principal else 'Secundario'
        return f"{self.estudiante} ← {self.acudiente} ({rol})"