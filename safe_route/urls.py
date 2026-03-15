from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('',            include('usuarios.urls')),
    path('estudiantes/',include('estudiantes.urls')),
    path('rutas/',      include('rutas.urls')),
    path('pagos/',      include('pagos.urls')),
]
