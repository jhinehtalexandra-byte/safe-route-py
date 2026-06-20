from django.db import models
from usuarios.models import Usuario
from estudiantes.models import Estudiante

class Notificacion(models.Model):

    TIPO = [
        ('RECOGIDA',        'Niño recogido en casa'),
        ('LLEGADA_COLEGIO', 'Llegada al colegio'),
        ('SALIDA_COLEGIO',  'Salida del colegio'),
        ('ENTREGA_CASA',    'Niño entregado en casa'),
        ('PAGO_EXITOSO',    'Pago confirmado'),
        ('PAGO_FALLIDO',    'Pago fallido'),
        ('AVISO_GENERAL',   'Aviso general'),
    ]

    CANAL = [
        ('APP',       'Notificación en la app'),
        ('WHATSAPP',  'WhatsApp'),
        ('SMS',       'SMS'),
        ('EMAIL',     'Correo electrónico'),
    ]

    ESTADO = [
        ('ENVIADA',  'Enviada correctamente'),
        ('FALLIDA',  'Falló el envío'),
        ('LEIDA',    'Leída por el padre'),
        ('PENDIENTE','Pendiente de envío'),
    ]

    # ── Quién recibe y sobre quién ─────────────────────────────────
    destinatario   = models.ForeignKey(
                        Usuario,
                        on_delete=models.CASCADE,
                        related_name='notificaciones',
                        limit_choices_to={'rol': 'PADRE'}
                     )
    estudiante     = models.ForeignKey(
                        Estudiante,
                        on_delete=models.CASCADE,
                        related_name='notificaciones',
                        null=True, blank=True   # null en pagos o avisos generales
                     )

    # ── Qué pasó ──────────────────────────────────────────────────
    tipo           = models.CharField(max_length=20, choices=TIPO)
    canal          = models.CharField(max_length=10, choices=CANAL, default='APP')
    estado         = models.CharField(max_length=10, choices=ESTADO, default='PENDIENTE')
    mensaje        = models.CharField(max_length=300)

    # ── Cuándo ────────────────────────────────────────────────────
    fecha_envio    = models.DateTimeField(auto_now_add=True)
    fecha_lectura  = models.DateTimeField(null=True, blank=True)

    # ── Metadata útil ─────────────────────────────────────────────
    latitud        = models.DecimalField(
                        max_digits=9, decimal_places=6,
                        null=True, blank=True   # ubicación GPS cuando se disparó
                     )
    longitud       = models.DecimalField(
                        max_digits=9, decimal_places=6,
                        null=True, blank=True
                     )
    error_detalle  = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = 'notificacion'
        ordering = ['-fecha_envio']   # más recientes primero

    def __str__(self):
        return f"{self.tipo} → {self.destinatario.nombre} ({self.estado})"

    @property
    def es_leida(self):
        return self.estado == 'LEIDA'