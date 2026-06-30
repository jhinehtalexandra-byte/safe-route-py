# rutas/models.py
from django.db import models
from usuarios.models import Usuario


# ============================================================
# RUTA
# ============================================================
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
    ZONA = [
        ('NORTE',     'Norte'),
        ('SUR',       'Sur'),
        ('ORIENTE',   'Oriente'),
        ('OCCIDENTE', 'Occidente'),
        ('CENTRO',    'Centro'),
    ]

    zona   = models.CharField(max_length=20, choices=ZONA, blank=True, null=True)
    activo = models.BooleanField(default=True)
    conductor_cedula = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column='conductor_cedula',   # ← columna real en BD
    )
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ruta'

    def __str__(self):
        return self.nombre


# ============================================================
# PARADA
# ============================================================
class Parada(models.Model):
    ruta       = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        related_name='paradas',
        db_column='ruta',               # ← columna real en BD
    )
    orden      = models.PositiveSmallIntegerField()
    nombre     = models.CharField(max_length=150)
    direccion  = models.CharField(max_length=300)
    referencia = models.CharField(max_length=200, blank=True, null=True)
    latitud    = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitud   = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    activo     = models.BooleanField(default=True)

    class Meta:
        db_table = 'parada'
        ordering = ['ruta', 'orden']
        unique_together = ('ruta', 'orden')

    def __str__(self):
        return f"{self.ruta.nombre} — Parada {self.orden}: {self.nombre}"


# ============================================================
# RECORRIDO
# ============================================================
class Recorrido(models.Model):
    ESTADO = [
        ('PENDIENTE',  'Pendiente'),
        ('EN_CURSO',   'En curso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO',  'Cancelado'),
    ]

    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        related_name='recorridos',
        db_column='ruta',               # ← evita que Django busque "ruta_id"
    )
    conductor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='recorridos_conductor',
        db_column='conductor',          # ← evita que Django busque "conductor_id"
    )
    monitora = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='recorridos_monitora',
        db_column='monitora',           # ← evita que Django busque "monitora_id"
    )
    fecha  = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO, default='PENDIENTE')

    hora_inicio_real        = models.DateTimeField(blank=True, null=True)
    hora_fin_real           = models.DateTimeField(blank=True, null=True)
    lista_confirmada        = models.BooleanField(default=False)
    hora_confirmacion_lista = models.DateTimeField(blank=True, null=True)

    ubicacion_lat                = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    ubicacion_lng                = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    ultima_ubicacion_actualizada = models.DateTimeField(blank=True, null=True)

    observaciones       = models.TextField(blank=True, null=True)
    fecha_creacion      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recorrido'
        ordering = ['-fecha', '-fecha_creacion']

    def __str__(self):
        return f"{self.ruta.nombre} — {self.fecha} ({self.estado})"


# ============================================================
# PARADA DE RECORRIDO
# ============================================================
class ParadaRecorrido(models.Model):
    ESTADO = [
        ('PENDIENTE',  'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('SALTADA',    'Saltada'),
    ]

    recorrido = models.ForeignKey(
        Recorrido,
        on_delete=models.CASCADE,
        related_name='paradas_recorrido',
        db_column='recorrido',          # ← columna real en BD
    )
    parada = models.ForeignKey(
        Parada,
        on_delete=models.CASCADE,
        related_name='recorridos_parada',
        db_column='parada',             # ← columna real en BD
    )
    estado       = models.CharField(max_length=15, choices=ESTADO, default='PENDIENTE')
    hora_llegada = models.DateTimeField(blank=True, null=True)
    observacion  = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = 'parada_recorrido'
        ordering = ['parada__orden']
        unique_together = ('recorrido', 'parada')

    def __str__(self):
        return f"{self.recorrido} | {self.parada.nombre} → {self.estado}"
    
    
    
    