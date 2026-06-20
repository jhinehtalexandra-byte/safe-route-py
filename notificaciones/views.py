# notificaciones/views.py
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import Notificacion


# ============================================================
# HELPERS
# ============================================================
def _sesion_activa(request):
    return bool(request.session.get('usuario_cedula'))


def _es_admin_o_colegio(request):
    return request.session.get('usuario_rol') in ('ADMIN', 'COLEGIO')


# ============================================================
# NOTIFICACIONES — Marcar como leída
# ============================================================
def marcar_leida(request, notif_id):
    if not _sesion_activa(request):
        return redirect('login')

    if request.method != 'POST':
        return redirect('notificaciones')

    cedula = request.session['usuario_cedula']

    try:
        if _es_admin_o_colegio(request):
            # ADMIN y COLEGIO pueden ver/gestionar todas las notificaciones,
            # igual que en la vista 'notificaciones' y 'marcar_todas_leidas'.
            notif = Notificacion.objects.get(id=notif_id)
        else:
            # Cualquier otro rol (PADRE, MONITORA, CONDUCTOR) solo puede
            # marcar como leídas sus propias notificaciones.
            notif = Notificacion.objects.get(
                id=notif_id,
                destinatario__cedula=cedula
            )

        notif.estado        = 'LEIDA'
        notif.fecha_lectura = timezone.now()
        notif.save()
        messages.success(request, 'Notificación marcada como leída.')

    except Notificacion.DoesNotExist:
        # Cubre tanto "no existe" como "existe pero no le pertenece al usuario"
        messages.error(request, 'Notificación no encontrada.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('notificaciones')