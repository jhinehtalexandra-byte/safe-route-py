import bcrypt
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
# HELPER — Correo de bienvenida con credenciales (usuario=cédula, pass=cédula)
# ──────────────────────────────────────────────────────────────
def _enviar_credenciales_conductor(nombre, email, cedula, dominio):
    """Envía correo de bienvenida al conductor con sus credenciales de acceso."""
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings as cfg

        asunto = '🚌 Bienvenido/a a SafeRoute — Tus credenciales de acceso'
        enlace = f'{dominio}/login/'

        texto_plano = (
            f'Hola {nombre},\n\n'
            f'Has sido registrado/a como conductor en SafeRoute.\n'
            f'Tu cuenta ya está activa. Tus credenciales son:\n\n'
            f'  Usuario:    {cedula}\n'
            f'  Contraseña: {cedula}\n'
            f'  Acceso:     {enlace}\n\n'
            f'Por seguridad, cambia tu contraseña después del primer ingreso.\n\n'
            f'Con tu cuenta podrás:\n'
            f'  • Ver tu ruta y paradas asignadas del día\n'
            f'  • Iniciar y finalizar tu recorrido\n'
            f'  • Notificar tu llegada a cada parada\n'
            f'  • Reportar novedades en tiempo real\n\n'
            f'— Equipo SafeRoute'
        )

        iniciales = ''.join([p[0].upper() for p in nombre.split()[:2]]) or 'CO'

        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f6f8fc;font-family:Arial,sans-serif;">
  <div style="max-width:520px;margin:32px auto;">

    <div style="background:#1e293b;border-radius:12px 12px 0 0;padding:28px;text-align:center;">
      <div style="font-size:36px;">🚌</div>
      <div style="font-size:20px;font-weight:800;color:white;margin-top:8px;">SafeRoute</div>
      <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;">
        Sistema de Gestión de Transporte Escolar
      </div>
      <div style="margin-top:20px;font-size:18px;font-weight:700;color:white;">¡Bienvenido/a a SafeRoute!</div>
      <div style="font-size:12px;color:#94a3b8;margin-top:4px;">Has sido registrado/a como conductor</div>
    </div>

    <div style="background:white;padding:28px;">
      <div style="font-size:16px;font-weight:700;color:#1f2937;margin-bottom:8px;">
        Hola, <span style="color:#3b82f6;">{nombre}</span> 👋
      </div>
      <p style="font-size:13px;color:#4b5563;line-height:1.6;margin:0 0 20px;">
        El colegio te ha registrado como conductor en el sistema de transporte escolar SafeRoute.
        Tu cuenta ya está activa y puedes ingresar ahora mismo.
      </p>

      <div style="background:#eff6ff;border:1.5px solid #bfdbfe;border-radius:10px;padding:16px;margin-bottom:20px;">
        <div style="font-size:10px;font-weight:700;color:#1d4ed8;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:12px;">
          Tus credenciales de acceso
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #dbeafe;">
          <span style="font-size:12px;color:#1d4ed8;">🔒 Usuario</span>
          <span style="font-size:13px;font-weight:700;color:#1e3a8a;font-family:monospace;">{cedula}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;">
          <span style="font-size:12px;color:#1d4ed8;">🔑 Contraseña</span>
          <span style="font-size:13px;font-weight:700;color:#1e3a8a;font-family:monospace;">{cedula}</span>
        </div>
      </div>

      <div style="text-align:center;margin:24px 0 20px;">
        <a href="{enlace}"
           style="display:inline-block;background:linear-gradient(135deg,#3b82f6,#1d4ed8);color:white;font-weight:700;font-size:14px;padding:14px 36px;border-radius:8px;text-decoration:none;">
          🚀 &nbsp; Ingresar a SafeRoute
        </a>
      </div>

      <div style="font-size:10px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">
        Con tu cuenta podrás:
      </div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Ver tu ruta y paradas asignadas del día</div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Iniciar y finalizar tu recorrido</div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Notificar tu llegada a cada parada</div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Reportar novedades en tiempo real</div>

      <div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;padding:12px 14px;font-size:11px;color:#92400e;line-height:1.6;margin-top:20px;">
        <strong>⚠️ Recomendación de seguridad:</strong> cambia tu contraseña después de tu primer ingreso.
      </div>
    </div>

    <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:14px 28px;text-align:center;font-size:11px;color:#6b7280;line-height:1.6;">
      🔒 Correo confidencial. Si recibiste este mensaje por error, ignóralo.
    </div>

    <div style="background:#1e293b;border-radius:0 0 12px 12px;padding:20px;text-align:center;">
      <div style="font-size:14px;font-weight:800;color:white;">🚌 SafeRoute</div>
      <div style="font-size:10px;color:#64748b;margin-top:8px;line-height:1.7;">
        Sistema de Gestión de Transporte Escolar<br>
        Bogotá D.C. · Colombia · © 2026 SafeRoute<br>
        Correo enviado a <span style="color:#94a3b8;">{email}</span>
      </div>
    </div>

  </div>
</body>
</html>"""

        correo = EmailMultiAlternatives(
            subject=asunto, body=texto_plano,
            from_email=getattr(cfg, 'DEFAULT_FROM_EMAIL', 'noreply@saferoute.co'),
            to=[email],
        )
        correo.attach_alternative(html, 'text/html')
        correo.send(fail_silently=True)
        return True
    except Exception as e:
        print(f'⚠️ No se pudo enviar correo a {email}: {e}')
        return False


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
    usuario, redir = _require_admin_o_colegio(request)
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

    nombre = p.get('nombre', '').strip()
    email  = p.get('email', '').strip().lower()

    # ── Usuario y contraseña se generan automáticamente: ambos = cédula ──
    user_name = cedula
    if Usuario.objects.filter(user_name=user_name).exists():
        messages.error(request, f'Ya existe un usuario con nombre de usuario "{user_name}".')
        return redirect('conductores')

    # Se usa bcrypt directamente (igual que el resto del sistema) para que
    # login_view (que usa bcrypt.checkpw) pueda verificar la contraseña.
    password_hash = bcrypt.hashpw(cedula.encode(), bcrypt.gensalt()).decode()

    try:
        u = Usuario(
            cedula         = cedula,
            tipo_documento = p.get('tipo_documento'),
            user_name      = user_name,
            password       = password_hash,
            nombre         = nombre,
            email          = email,
            telefono       = p.get('telefono', '').strip() or None,
            rol            = 'CONDUCTOR',
            activo         = True,
        )
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

        dominio   = request.build_absolute_uri('/')[:-1]
        correo_ok = _enviar_credenciales_conductor(nombre, email, cedula, dominio)

        if correo_ok:
            messages.success(request, f'Conductor {nombre} registrado. Credenciales enviadas a {email}.')
        else:
            messages.warning(
                request,
                f'Conductor {nombre} registrado, pero no se pudo enviar el correo con las credenciales. '
                f'Usuario: {cedula} / Contraseña: {cedula}.'
            )

    except Exception as e:
        messages.error(request, f'Error al registrar conductor: {e}')

    return redirect('conductores')


# ──────────────────────────────────────────────────────────────
# EDITAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def conductor_editar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)
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
# ELIMINAR (soft delete)
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def conductor_eliminar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)
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