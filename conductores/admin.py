from django.contrib import admin
from .models import Conductor


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'placa', 'categoria_licencia', 'fecha_vencimiento_lic')
    search_fields = ('usuario__nombre', 'placa', 'numero_licencia')
    list_filter   = ('categoria_licencia', 'tipo_vehiculo')