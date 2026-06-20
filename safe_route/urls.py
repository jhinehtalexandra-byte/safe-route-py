# safe_route/urls.py
from django.contrib import admin
from django.urls import path, include

# handler404 se declara aquí pero apunta a la vista de usuarios
handler404 = 'usuarios.views.error_404'

urlpatterns = [
    # Panel de administración de Django (opcional, útil para crear usuarios de prueba)
    path('admin/', admin.site.urls),

    # ─────────────────────────────────────────────────────────────────
    # TODAS las rutas van en usuarios/urls.py
    # NO incluyas prefijos de otras apps aquí para evitar duplicación.
    # usuarios/urls.py ya importa directamente las vistas de cada app.
    # ─────────────────────────────────────────────────────────────────
    path('', include('usuarios.urls')),
]