from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.lista_estudiantes,   name='estudiantes'),
    path('nuevo/',                        views.nuevo_estudiante,    name='estudiante_nuevo'),
    path('<str:documento>/editar/',       views.estudiante_editar,   name='estudiante_editar'),
    path('<str:documento>/eliminar/',     views.estudiante_eliminar, name='estudiante_eliminar'),
    path('pdf/',                          views.estudiantes_pdf,     name='estudiantes_pdf'),
    path('excel/',                        views.estudiantes_excel,   name='estudiantes_excel'),
]