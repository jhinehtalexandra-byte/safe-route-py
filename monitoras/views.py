import bcrypt
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
# HELPER — Correo de bienvenida con credenciales (usuario=cédula, pass=cédula)
# ──────────────────────────────────────────────────────────────
def _enviar_credenciales_monitora(nombre, email, cedula, dominio):
    """Envía correo de bienvenida a la monitora con sus credenciales de acceso."""
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings as cfg

        asunto = '🚌 Bienvenida a SafeRoute — Tus credenciales de acceso'
        enlace = f'{dominio}/login/'

        texto_plano = (
            f'Hola {nombre},\n\n'
            f'Has sido registrada como monitora en SafeRoute.\n'
            f'Tu cuenta ya está activa. Tus credenciales son:\n\n'
            f'  Usuario:    {cedula}\n'
            f'  Contraseña: {cedula}\n'
            f'  Acceso:     {enlace}\n\n'
            f'Por seguridad, cambia tu contraseña después del primer ingreso.\n\n'
            f'Con tu cuenta podrás:\n'
            f'  • Confirmar la lista de estudiantes antes de iniciar el recorrido\n'
            f'  • Registrar novedades y ausencias\n'
            f'  • Solicitar autorización de datos médicos\n'
            f'  • Recibir alertas del recorrido en tiempo real\n\n'
            f'— Equipo SafeRoute'
        )

        iniciales = ''.join([p[0].upper() for p in nombre.split()[:2]]) or 'MO'

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
      <div style="margin-top:20px;font-size:18px;font-weight:700;color:white;">¡Bienvenida a SafeRoute!</div>
      <div style="font-size:12px;color:#94a3b8;margin-top:4px;">Has sido registrada como monitora</div>
    </div>

    <div style="background:white;padding:28px;">
      <div style="font-size:16px;font-weight:700;color:#1f2937;margin-bottom:8px;">
        Hola, <span style="color:#be185d;">{nombre}</span> 👋
      </div>
      <p style="font-size:13px;color:#4b5563;line-height:1.6;margin:0 0 20px;">
        El colegio te ha registrado como monitora en el sistema de transporte escolar SafeRoute.
        Tu cuenta ya está activa y puedes ingresar ahora mismo.
      </p>

      <div style="background:#fdf2f8;border:1.5px solid #fbcfe8;border-radius:10px;padding:16px;margin-bottom:20px;">
        <div style="font-size:10px;font-weight:700;color:#be185d;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:12px;">
          Tus credenciales de acceso
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #fce7f3;">
          <span style="font-size:12px;color:#be185d;">🔒 Usuario</span>
          <span style="font-size:13px;font-weight:700;color:#831843;font-family:monospace;">{cedula}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;">
          <span style="font-size:12px;color:#be185d;">🔑 Contraseña</span>
          <span style="font-size:13px;font-weight:700;color:#831843;font-family:monospace;">{cedula}</span>
        </div>
      </div>

      <div style="text-align:center;margin:24px 0 20px;">
        <a href="{enlace}"
           style="display:inline-block;background:linear-gradient(135deg,#ec4899,#be185d);color:white;font-weight:700;font-size:14px;padding:14px 36px;border-radius:8px;text-decoration:none;">
          🚀 &nbsp; Ingresar a SafeRoute
        </a>
      </div>

      <div style="font-size:10px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">
        Con tu cuenta podrás:
      </div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#be185d;font-weight:700;">✓</span> &nbsp;Confirmar la lista de estudiantes antes del recorrido</div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#be185d;font-weight:700;">✓</span> &nbsp;Registrar novedades y ausencias</div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#be185d;font-weight:700;">✓</span> &nbsp;Solicitar autorización de datos médicos</div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;"><span style="color:#be185d;font-weight:700;">✓</span> &nbsp;Recibir alertas del recorrido en tiempo real</div>

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
    usuario, redir = _require_admin_o_colegio(request)
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

    nombre = p.get('nombre', '').strip()
    email  = p.get('email', '').strip().lower()

    # ── Usuario y contraseña se generan automáticamente: ambos = cédula ──
    user_name = cedula
    if Usuario.objects.filter(user_name=user_name).exists():
        messages.error(request, f'Ya existe un usuario con nombre de usuario "{user_name}".')
        return redirect('monitoras')

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
            rol            = 'MONITORA',
            activo         = True,
        )
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

        dominio   = request.build_absolute_uri('/')[:-1]
        correo_ok = _enviar_credenciales_monitora(nombre, email, cedula, dominio)

        if correo_ok:
            messages.success(request, f'Monitora {nombre} registrada. Credenciales enviadas a {email}.')
        else:
            messages.warning(
                request,
                f'Monitora {nombre} registrada, pero no se pudo enviar el correo con las credenciales. '
                f'Usuario: {cedula} / Contraseña: {cedula}.'
            )

    except Exception as e:
        messages.error(request, f'Error al registrar monitora: {e}')

    return redirect('monitoras')


# ──────────────────────────────────────────────────────────────
# EDITAR
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def monitora_editar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)
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
# ELIMINAR (soft delete)
# ──────────────────────────────────────────────────────────────
@transaction.atomic
def monitora_eliminar(request, cedula):
    usuario, redir = _require_admin_o_colegio(request)
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