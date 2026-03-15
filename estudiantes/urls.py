from django.urls import path
from . import views

urlpatterns = [
    path('',        views.lista_estudiantes, name='estudiantes'),
    path('nuevo/',  views.nuevo_estudiante,  name='estudiante_nuevo'),
]