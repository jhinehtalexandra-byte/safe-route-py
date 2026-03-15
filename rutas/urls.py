from django.urls import path
from . import views

urlpatterns = [
    path('',      views.lista_rutas,   name='rutas'),
    path('mapa/', views.mapa_conductor,name='mapa_conductor'),
]