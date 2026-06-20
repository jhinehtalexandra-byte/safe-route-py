from django.urls import path
from . import views

urlpatterns = [
    path('monitoras/',                        views.lista_monitoras, name='monitoras'),
    path('monitoras/nueva/',                  views.monitora_nueva,  name='monitora_nueva'),
    path('monitoras/editar/<str:cedula>/',    views.monitora_editar, name='monitora_editar'),
    path('monitoras/eliminar/<str:cedula>/',  views.monitora_eliminar,name='monitora_eliminar'),
]