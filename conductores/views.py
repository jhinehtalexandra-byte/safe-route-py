from django.shortcuts      import render, redirect, get_object_or_404
from django.contrib        import messages
from django.db             import transaction
from django.utils          import timezone

from usuarios.models       import Usuario
from .models               import Conductor
from rutas.models          import Ruta


# ──────────────────────────────────────────────────────────────
# Helper: sesión activa y rol
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
    """Retorna (usuario, None) si es admin, o (None, redirect) si no lo es."""
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
def lista_conductores(request):
    usuario, redir = _require_admin_o_colegio(request)
    if redir:
        return redir

    # Filtros GET
    nombre     = request.GET.get('nombre',    '').strip()
    placa      = request.GET.get('placa',     '').strip()
    categoria  = request.GET.get('categoria', '').strip()
    activo_str = request.GET.get('activo',    'true').strip()
    ruta_cod   = request.GET.get('ruta',      '').strip()
    soat_str   = request.GET.get('soat',      '').strip()
    tecno_str  = request.GET.get('tecno',     '').strip()

    hoy = timezone.now().date()

    qs = Conductor.objects.select_related('usuario').all()

    if nombre:
        qs = qs.filter(usuario__nombre__icontains=nombre)
    if placa:
        qs = qs.filter(placa__icontains=placa)
    if categoria:
        qs = qs.filter(categoria_licencia=categoria)
    if activo_str in ('true', 'false'):
        qs = qs.filter(usuario__activo=(activo_str == 'true'))
    if ruta_cod:
        cedulas = Ruta.objects.filter(codigo=ruta_cod).values_list(
            'conductor_cedula', flat=True)
        qs = qs.filter(usuario__cedula__in=cedulas)
    if soat_str == 'vencido':
        qs = qs.filter(fecha_vencimiento_soat__lt=hoy)
    elif soat_str == 'vigente':
        qs = qs.filter(fecha_vencimiento_soat__gte=hoy)
    if tecno_str == 'vencida':
        qs = qs.filter(fecha_vencimiento_tecno__lt=hoy)
    elif tecno_str == 'vigente':
        qs = qs.filter(fecha_vencimiento_tecno__gte=hoy)

    # Estadísticas
    total     = Conductor.objects.count()
    activos   = Conductor.objects.filter(usuario__activo=True).count()
    lic_venc  = Conductor.objects.filter(fecha_vencimiento_lic__lt=hoy).count()
    soat_venc = Conductor.objects.filter(
        fecha_vencimiento_soat__isnull=False,
        fecha_vencimiento_soat__lt=hoy
    ).count()

    rutas = Ruta.objects.filter(activo=True).order_by('nombre')

    context = {
        'conductores':         qs,
        'rutas':               rutas,
        'nombre':              nombre,
        'placa':               placa,
        'categoria':           categoria,
        'activo':              activo_str,
        'ruta':                ruta_cod,
        'soat':                soat_str,
        'tecno':               tecno_str,
        'total_conductores':   total,
        'conductores_activos': activos,
        'licencias_vencidas':  lic_venc,
        'soat_vencidos':       soat_venc,
        'categorias':          Conductor.CATEGORIA_LICENCIA,
        'tipos_vehiculo':      Conductor.TIPO_VEHICULO,
        'usuario_nombre':      usuario.nombre,
        'usuario_rol':         usuario.rol,
    }
    return render(request, 'conductores/lista_conductores.html', context)


# ──────────────────────────────────────────────────────────────
# CREAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def conductor_nuevo(request):
    usuario, redir = _require_admin_o_colegio(request)   # ← cambiado
    if redir:
        return redir

    if request.method != 'POST':
        return redirect('conductores')

    p = request.POST

    cedula = p.get('cedula', '').strip()
    if not cedula:
        messages.error(request, 'La cédula es obligatoria.')
        return redirect('conductores')

    if Usuario.objects.filter(cedula=cedula).exists():
        messages.error(request, f'Ya existe un usuario con cédula {cedula}.')
        return redirect('conductores')

    placa = p.get('placa', '').strip().upper()
    if Conductor.objects.filter(placa=placa).exists():
        messages.error(request, f'La placa {placa} ya está registrada.')
        return redirect('conductores')

    numero_licencia = p.get('numero_licencia', '').strip()
    if Conductor.objects.filter(numero_licencia=numero_licencia).exists():
        messages.error(request, f'La licencia {numero_licencia} ya está registrada.')
        return redirect('conductores')

    user_name = p.get('user_name', '').strip()
    if not user_name:
        messages.error(request, 'El nombre de usuario es obligatorio.')
        return redirect('conductores')

    raw_pass = p.get('password', '').strip()
    if not raw_pass:
        messages.error(request, 'La contraseña es obligatoria.')
        return redirect('conductores')

    try:
        u = Usuario(
            cedula         = cedula,
            tipo_documento = p.get('tipo_documento'),
            user_name      = user_name,
            nombre         = p.get('nombre', '').strip(),
            email          = p.get('email', '').strip(),
            telefono       = p.get('telefono', '').strip() or None,
            rol            = 'CONDUCTOR',
            activo         = True,
        )
        u.set_password(raw_pass)
        u.save()

        Conductor.objects.create(
            usuario                 = u,
            numero_licencia         = numero_licencia,
            categoria_licencia      = p.get('categoria_licencia'),
            fecha_expedicion_lic    = p.get('fecha_expedicion_lic'),
            fecha_vencimiento_lic   = p.get('fecha_vencimiento_lic'),
            lugar_expedicion_lic    = p.get('lugar_expedicion_lic', '').strip() or None,
            placa                   = placa,
            tipo_vehiculo           = p.get('tipo_vehiculo'),
            marca_vehiculo          = p.get('marca_vehiculo', '').strip(),
            modelo_vehiculo         = p.get('modelo_vehiculo', '').strip(),
            anio_vehiculo           = int(p.get('anio_vehiculo', 2020)),
            color_vehiculo          = p.get('color_vehiculo', '').strip() or None,
            capacidad_pasajeros     = int(p['capacidad_pasajeros']) if p.get('capacidad_pasajeros') else None,
            numero_soat             = p.get('numero_soat', '').strip() or None,
            fecha_vencimiento_soat  = p.get('fecha_vencimiento_soat') or None,
            numero_tecnomecanica    = p.get('numero_tecnomecanica', '').strip() or None,
            fecha_vencimiento_tecno = p.get('fecha_vencimiento_tecno') or None,
            anios_experiencia       = int(p.get('anios_experiencia', 0) or 0),
            observaciones           = p.get('observaciones', '').strip() or None,
        )

        messages.success(request, f'Conductor {u.nombre} registrado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al registrar conductor: {e}')

    return redirect('conductores')


# ──────────────────────────────────────────────────────────────
# EDITAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def conductor_editar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)   # ← cambiado
    if redir:
        return redir

    conductor = get_object_or_404(Conductor, usuario__cedula=cedula)

    if request.method == 'POST':
        p = request.POST
        try:
            u = conductor.usuario
            u.nombre   = p.get('nombre',   u.nombre).strip()
            u.email    = p.get('email',    u.email).strip()
            u.telefono = p.get('telefono', u.telefono or '').strip() or None
            u.activo   = p.get('activo') == 'true'
            u.save()

            placa = p.get('placa', '').strip().upper()
            if placa and placa != conductor.placa:
                if Conductor.objects.filter(placa=placa).exclude(usuario__cedula=cedula).exists():
                    messages.error(request, f'La placa {placa} ya está registrada en otro conductor.')
                    return redirect('conductores')
                conductor.placa = placa

            conductor.numero_licencia         = p.get('numero_licencia', conductor.numero_licencia)
            conductor.categoria_licencia      = p.get('categoria_licencia', conductor.categoria_licencia)
            conductor.fecha_expedicion_lic    = p.get('fecha_expedicion_lic') or conductor.fecha_expedicion_lic
            conductor.fecha_vencimiento_lic   = p.get('fecha_vencimiento_lic') or conductor.fecha_vencimiento_lic
            conductor.lugar_expedicion_lic    = p.get('lugar_expedicion_lic', '').strip() or None
            conductor.tipo_vehiculo           = p.get('tipo_vehiculo', conductor.tipo_vehiculo)
            conductor.marca_vehiculo          = p.get('marca_vehiculo', conductor.marca_vehiculo).strip()
            conductor.modelo_vehiculo         = p.get('modelo_vehiculo', conductor.modelo_vehiculo).strip()
            conductor.anio_vehiculo           = int(p.get('anio_vehiculo', conductor.anio_vehiculo))
            conductor.color_vehiculo          = p.get('color_vehiculo', '').strip() or None
            conductor.capacidad_pasajeros     = int(p['capacidad_pasajeros']) if p.get('capacidad_pasajeros') else None
            conductor.numero_soat             = p.get('numero_soat', '').strip() or None
            conductor.fecha_vencimiento_soat  = p.get('fecha_vencimiento_soat') or None
            conductor.numero_tecnomecanica    = p.get('numero_tecnomecanica', '').strip() or None
            conductor.fecha_vencimiento_tecno = p.get('fecha_vencimiento_tecno') or None
            conductor.anios_experiencia       = int(p.get('anios_experiencia', 0) or 0)
            conductor.observaciones           = p.get('observaciones', '').strip() or None
            conductor.save()

            messages.success(request, f'Conductor {u.nombre} actualizado correctamente.')
            return redirect('conductores')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')

    rutas = Ruta.objects.filter(activo=True).order_by('nombre')
    context = {
        'es_nuevo':                      False,
        'conductor':                     conductor,
        'rutas':                         rutas,
        'categorias':                    Conductor.CATEGORIA_LICENCIA,
        'tipos_vehiculo':                Conductor.TIPO_VEHICULO,
        'fecha_actual':                  timezone.now().date(),
        'usuario_nombre':                usuario.nombre,
        'usuario_rol':                   request.session.get('usuario_rol'),
        'tipo_documento_previo':         '',
        'categoria_licencia_previo':     '',
        'tipo_vehiculo_previo':          '',
    }
    return render(request, 'conductores/nuevo_conductor.html', context)


# ──────────────────────────────────────────────────────────────
# ELIMINAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def conductor_eliminar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)   # ← cambiado
    if redir:
        return redir

    conductor = get_object_or_404(Conductor, usuario__cedula=cedula)

    if request.method == 'POST':
        try:
            nombre = conductor.usuario.nombre
            conductor.usuario.activo = False
            conductor.usuario.save(update_fields=['activo'])
            messages.success(request, f'Conductor {nombre} desactivado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al desactivar: {e}')

    return redirect('conductores')
# ──────────────────────────────────────────────────────────────
# REACTIVAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def conductor_reactivar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)
    if redir:
        return redir

    conductor = get_object_or_404(Conductor, usuario__cedula=cedula)

    if request.method == 'POST':
        try:
            conductor.usuario.activo = True
            conductor.usuario.save(update_fields=['activo'])
            messages.success(request, f'Conductor {conductor.usuario.nombre} reactivado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al reactivar: {e}')

    return redirect('conductores')