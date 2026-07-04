from django.shortcuts  import render, redirect, get_object_or_404
from django.contrib    import messages
from django.db         import transaction
from django.utils      import timezone

from usuarios.models   import Usuario
from .models           import Monitora
from rutas.models      import Ruta


# ──────────────────────────────────────────────────────────────
# Helpers de sesión
# ──────────────────────────────────────────────────────────────
def _get_usuario(request):
    cedula = request.session.get('usuario_cedula')
    if not cedula:
        return None
    try:
        return Usuario.objects.get(cedula=cedula)
    except Usuario.DoesNotExist:
        return None


def _require_admin(request):
    u = _get_usuario(request)
    if not u:
        return None, redirect('login')
    if not u.es_admin:
        return None, redirect('dashboard_' + u.rol.lower())
    return u, None


def _require_admin_o_colegio(request):
    u = _get_usuario(request)
    if not u:
        return None, redirect('login')
    if u.rol not in ('ADMIN', 'COLEGIO'):
        return None, redirect('dashboard_' + u.rol.lower())
    return u, None


# ──────────────────────────────────────────────────────────────
# LISTA + BÚSQUEDA
# ──────────────────────────────────────────────────────────────
def lista_monitoras(request):
    usuario, redir = _require_admin_o_colegio(request)
    if redir:
        return redir

    nombre     = request.GET.get('nombre',     '').strip()
    activo_str = request.GET.get('activo',     'true').strip()
    ruta_cod   = request.GET.get('ruta',       '').strip()
    cert_str   = request.GET.get('certificado','').strip()

    qs = Monitora.objects.select_related('usuario', 'ruta_asignada').all()

    if nombre:
        qs = qs.filter(usuario__nombre__icontains=nombre)
    if activo_str in ('true', 'false'):
        qs = qs.filter(usuario__activo=(activo_str == 'true'))
    if ruta_cod:
        qs = qs.filter(ruta_asignada__codigo=ruta_cod)
    if cert_str == 'true':
        qs = qs.filter(tiene_certificado_pa=True)
    elif cert_str == 'false':
        qs = qs.filter(tiene_certificado_pa=False)

    total    = Monitora.objects.count()
    activas  = Monitora.objects.filter(usuario__activo=True).count()
    con_cert = Monitora.objects.filter(tiene_certificado_pa=True).count()
    sin_ruta = Monitora.objects.filter(ruta_asignada__isnull=True).count()

    rutas = Ruta.objects.filter(activo=True).order_by('nombre')

    context = {
        'monitoras':           qs,
        'rutas':               rutas,
        'nombre':              nombre,
        'activo':              activo_str,
        'ruta':                ruta_cod,
        'certificado':         cert_str,
        'total_monitoras':     total,
        'monitoras_activas':   activas,
        'con_certificado':     con_cert,
        'sin_ruta':            sin_ruta,
        'niveles_educativos':  Monitora.NIVEL_EDUCATIVO,
        'usuario_nombre':      usuario.nombre,
        'usuario_rol':         usuario.rol,
    }
    return render(request, 'monitoras/lista_monitoras.html', context)


# ──────────────────────────────────────────────────────────────
# CREAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def monitora_nueva(request):
    usuario, redir = _require_admin_o_colegio(request)   # ← cambiado
    if redir:
        return redir

    if request.method != 'POST':
        return redirect('monitoras')

    p = request.POST

    cedula = p.get('cedula', '').strip()
    if not cedula:
        messages.error(request, 'La cédula es obligatoria.')
        return redirect('monitoras')

    if Usuario.objects.filter(cedula=cedula).exists():
        messages.error(request, f'Ya existe un usuario con cédula {cedula}.')
        return redirect('monitoras')

    user_name = p.get('user_name', '').strip()
    if not user_name:
        messages.error(request, 'El nombre de usuario es obligatorio.')
        return redirect('monitoras')

    raw_pass = p.get('password', '').strip()
    if not raw_pass:
        messages.error(request, 'La contraseña es obligatoria.')
        return redirect('monitoras')

    try:
        u = Usuario(
            cedula         = cedula,
            tipo_documento = p.get('tipo_documento'),
            user_name      = user_name,
            nombre         = p.get('nombre', '').strip(),
            email          = p.get('email', '').strip(),
            telefono       = p.get('telefono', '').strip() or None,
            rol            = 'MONITORA',
            activo         = True,
        )
        u.set_password(raw_pass)
        u.save()

        ruta_obj = None
        ruta_cod = p.get('ruta_asignada', '').strip()
        if ruta_cod:
            try:
                ruta_obj = Ruta.objects.get(codigo=ruta_cod)
            except Ruta.DoesNotExist:
                pass

        Monitora.objects.create(
            usuario                  = u,
            tiene_certificado_pa     = p.get('tiene_certificado_pa') == 'on',
            entidad_certificadora_pa = p.get('entidad_certificadora_pa', '').strip() or None,
            fecha_certificado_pa     = p.get('fecha_certificado_pa') or None,
            fecha_vencimiento_pa     = p.get('fecha_vencimiento_pa') or None,
            nivel_educativo          = p.get('nivel_educativo') or None,
            anios_experiencia        = int(p.get('anios_experiencia', 0) or 0),
            ruta_asignada            = ruta_obj,
            observaciones            = p.get('observaciones', '').strip() or None,
        )

        messages.success(request, f'Monitora {u.nombre} registrada correctamente.')
    except Exception as e:
        messages.error(request, f'Error al registrar monitora: {e}')

    return redirect('monitoras')


# ──────────────────────────────────────────────────────────────
# EDITAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def monitora_editar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)   # ← cambiado
    if redir:
        return redir

    monitora = get_object_or_404(Monitora, usuario__cedula=cedula)

    if request.method == 'POST':
        p = request.POST
        try:
            u = monitora.usuario
            u.nombre   = p.get('nombre',   u.nombre).strip()
            u.email    = p.get('email',    u.email).strip()
            u.telefono = p.get('telefono', u.telefono or '').strip() or None
            u.activo   = p.get('activo') == 'true'
            u.save()

            ruta_obj = None
            ruta_cod = p.get('ruta_asignada', '').strip()
            if ruta_cod:
                try:
                    ruta_obj = Ruta.objects.get(codigo=ruta_cod)
                except Ruta.DoesNotExist:
                    pass

            monitora.tiene_certificado_pa     = p.get('tiene_certificado_pa') == 'on'
            monitora.entidad_certificadora_pa = p.get('entidad_certificadora_pa', '').strip() or None
            monitora.fecha_certificado_pa     = p.get('fecha_certificado_pa') or None
            monitora.fecha_vencimiento_pa     = p.get('fecha_vencimiento_pa') or None
            monitora.nivel_educativo          = p.get('nivel_educativo') or None
            monitora.anios_experiencia        = int(p.get('anios_experiencia', 0) or 0)
            monitora.ruta_asignada            = ruta_obj
            monitora.observaciones            = p.get('observaciones', '').strip() or None
            monitora.save()

            messages.success(request, f'Monitora {u.nombre} actualizada correctamente.')
            return redirect('monitoras')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')

    rutas = Ruta.objects.filter(activo=True).order_by('nombre')
    context = {
        'es_nuevo':               False,
        'monitora':               monitora,
        'rutas':                  rutas,
        'niveles_educativos':     Monitora.NIVEL_EDUCATIVO,
        'fecha_actual':           timezone.now().date(),
        'usuario_nombre':         usuario.nombre,
        'usuario_rol':            usuario.rol,
        'tipo_documento_previo':  '',
        'nivel_educativo_previo': '',
    }
    return render(request, 'monitoras/nueva_monitora.html', context)


# ──────────────────────────────────────────────────────────────
# ELIMINAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def monitora_eliminar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)   # ← cambiado
    if redir:
        return redir

    monitora = get_object_or_404(Monitora, usuario__cedula=cedula)

    if request.method == 'POST':
        try:
            nombre = monitora.usuario.nombre
            monitora.usuario.activo = False
            monitora.usuario.save(update_fields=['activo'])
            messages.success(request, f'Monitora {nombre} desactivada correctamente.')
        except Exception as e:
            messages.error(request, f'Error al desactivar: {e}')

    return redirect('monitoras')

# ──────────────────────────────────────────────────────────────
# REACTIVAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def monitora_reactivar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)
    if redir:
        return redir

    monitora = get_object_or_404(Monitora, usuario__cedula=cedula)

    if request.method == 'POST':
        try:
            monitora.usuario.activo = True
            monitora.usuario.save(update_fields=['activo'])
            messages.success(request, f'Monitora {monitora.usuario.nombre} reactivada correctamente.')
        except Exception as e:
            messages.error(request, f'Error al reactivar: {e}')

    return redirect('monitoras')