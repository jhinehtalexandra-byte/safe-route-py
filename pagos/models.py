from django.db import models
from usuarios.models import Usuario
from estudiantes.models import Estudiante

class Pago(models.Model):
    ESTADO = [
        ('PAGADO',    'Pagado'),
        ('PENDIENTE', 'Pendiente'),
        ('VENCIDO',   'Vencido'),
        ('CANCELADO', 'Cancelado'),
    ]
    METODO = [
        ('EFECTIVO',      'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('TARJETA',       'Tarjeta'),
        ('NEQUI',         'Nequi'),
        ('DAVIPLATA',     'Daviplata'),
    ]

    codigo               = models.CharField(max_length=50, primary_key=True)
    monto                = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago           = models.DateField()
    fecha_vencimiento    = models.DateField(blank=True, null=True)
    estado               = models.CharField(max_length=20, choices=ESTADO)
    metodo_pago          = models.CharField(max_length=50, choices=METODO, blank=True, null=True)
    mes                  = models.CharField(max_length=20, blank=True, null=True)
    anio                 = models.IntegerField(blank=True, null=True)
    concepto             = models.CharField(max_length=500, blank=True, null=True)
    comprobante          = models.CharField(max_length=100, blank=True, null=True)
    documento_estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        db_column='documento_estudiante'
    )
    cedula_padre         = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='cedula_padre'
    )
    fecha_registro      = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pago'

    def __str__(self):
        return f"{self.codigo} - {self.estado}"