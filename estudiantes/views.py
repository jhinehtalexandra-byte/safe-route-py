from django.shortcuts import render
from .models import Estudiante

def lista_estudiantes(request):
    estudiantes = Estudiante.objects.filter(activo=True)
    return render(request, 'estudiantes/lista_estudiantes.html', {
        'estudiantes': estudiantes
    })

def nuevo_estudiante(request):
    return render(request, 'estudiantes/nuevo_estudiante.html')