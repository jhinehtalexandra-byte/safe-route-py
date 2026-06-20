from django.contrib import admin
from .models import Monitora


@admin.register(Monitora)
class MonitoraAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'ruta_asignada', 'tiene_certificado_pa', 'anios_experiencia')
    search_fields = ('usuario__nombre', 'ruta_asignada__nombre')
    list_filter   = ('tiene_certificado_pa', 'nivel_educativo')