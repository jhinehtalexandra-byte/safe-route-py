from django.urls import path
from . import views

urlpatterns = [
    path('conductores/',                        views.lista_conductores, name='conductores'),
    path('conductores/nuevo/',                  views.conductor_nuevo,   name='conductor_nuevo'),
    path('conductores/editar/<str:cedula>/',    views.conductor_editar,  name='conductor_editar'),
    path('conductores/eliminar/<str:cedula>/',  views.conductor_eliminar,name='conductor_eliminar'),
]