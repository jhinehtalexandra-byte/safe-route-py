from django.shortcuts import render
from .models import Ruta

def lista_rutas(request):
    rutas = Ruta.objects.filter(activo=True)
    return render(request, 'rutas/lista_rutas.html', {
        'rutas': rutas
    })

def mapa_conductor(request):
    return render(request, 'rutas/mapa_conductor.html')