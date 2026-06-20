# colegios/colegios_views.py
import bcrypt
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings as django_settings
from usuarios.models import Usuario


def _solo_admin(request):
    return (
        bool(request.session.get('usuario_cedula')) and
        request.session.get('usuario_rol') == 'ADMIN'
    )


# ── Todas las variables que el template necesita en GET ──────
def _ctx_nuevo_vacio(request):
    return {
        'es_nuevo':                   True,
        'colegio':                    None,
        'nit_previo':                 '',
        'nombre_institucion_previo':  '',
        'tipo_institucion_previo':    '',
        'codigo_dane_previo':         '',
        'direccion_previo':           '',
        'ciudad_previo':              '',
        'departamento_previo':        '',
        'telefono_previo':            '',
        'email_institucional_previo': '',
        'sitio_web_previo':           '',
        'nombre_rector_previo':       '',
        'telefono_rector_previo':     '',
        'email_rector_previo':        '',
        'user_name_previo':           '',
        'usuario_nombre':             request.session.get('usuario_nombre'),
        'usuario_rol':                request.session.get('usuario_rol'),
        'fecha_actual':               date.today(),
    }


def _ctx_nuevo_previo(request, post):
    return {
        'es_nuevo':                   True,
        'colegio':                    None,
        'nit_previo':                 post.get('nit', ''),
        'nombre_institucion_previo':  post.get('nombre_institucion', ''),
        'tipo_institucion_previo':    post.get('tipo_institucion', ''),
        'codigo_dane_previo':         post.get('codigo_dane', ''),
        'direccion_previo':           post.get('direccion', ''),
        'ciudad_previo':              post.get('ciudad', ''),
        'departamento_previo':        post.get('departamento', ''),
        'telefono_previo':            post.get('telefono', ''),
        'email_institucional_previo': post.get('email_institucional', ''),
        'sitio_web_previo':           post.get('sitio_web', ''),
        'nombre_rector_previo':       post.get('nombre_rector', ''),
        'telefono_rector_previo':     post.get('telefono_rector', ''),
        'email_rector_previo':        post.get('email_rector', ''),
        'user_name_previo':           post.get('user_name', ''),
        'usuario_nombre':             request.session.get('usuario_nombre'),
        'usuario_rol':                request.session.get('usuario_rol'),
        'fecha_actual':               date.today(),
    }


def _ctx_editar(request, colegio):
    return {
        'es_nuevo':                   False,
        'colegio':                    colegio,
        'nit_previo':                 '',
        'nombre_institucion_previo':  '',
        'tipo_institucion_previo':    '',
        'codigo_dane_previo':         '',
        'direccion_previo':           '',
        'ciudad_previo':              '',
        'departamento_previo':        '',
        'telefono_previo':            '',
        'email_institucional_previo': '',
        'sitio_web_previo':           '',
        'nombre_rector_previo':       '',
        'telefono_rector_previo':     '',
        'email_rector_previo':        '',
        'user_name_previo':           '',
        'usuario_nombre':             request.session.get('usuario_nombre'),
        'usuario_rol':                request.session.get('usuario_rol'),
        'fecha_actual':               date.today(),
    }


# ============================================================
# HELPERS — correos HTML
# ============================================================
def _enviar_correo_bienvenida_colegio(nombre_institucion, nombre_rector,
                                      email_destino, user_name, password_plano, dominio):
    try:
        asunto = '🏫 Bienvenido a SafeRoute — Credenciales de acceso'

        texto_plano = (
            f'Estimado/a {nombre_rector},\n\n'
            f'El sistema SafeRoute ha registrado exitosamente a {nombre_institucion}.\n\n'
            f'  Usuario:    {user_name}\n'
            f'  Contraseña: {password_plano}\n'
            f'  Acceso:     {dominio}/login/\n\n'
            f'Por seguridad, cambie la contraseña en su primer inicio de sesión.\n\n'
            f'— Equipo SafeRoute'
        )

        iniciales = ''.join(p[0].upper() for p in nombre_institucion.split()[:2]) or 'SR'

        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f6f8fc;font-family:Arial,sans-serif;">
  <div style="max-width:520px;margin:32px auto;">

    <!-- ENCABEZADO -->
    <div style="background:linear-gradient(135deg,#1e293b,#334155);border-radius:12px 12px 0 0;padding:28px;text-align:center;">
      <div style="font-size:36px;">🚌</div>
      <div style="font-size:20px;font-weight:800;color:white;margin-top:8px;">SafeRoute</div>
      <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;">
        Sistema de Gestión de Transporte Escolar
      </div>
      <div style="margin-top:20px;font-size:18px;font-weight:700;color:white;">
        ¡Bienvenido a SafeRoute! 🎉
      </div>
      <div style="font-size:12px;color:#94a3b8;margin-top:4px;">
        Tu institución ha sido registrada exitosamente
      </div>
    </div>

    <!-- CUERPO -->
    <div style="background:white;padding:28px;">

      <!-- Saludo -->
      <div style="font-size:16px;font-weight:700;color:#1f2937;margin-bottom:8px;">
        Estimado/a <span style="color:#f59e0b;">{nombre_rector}</span> 👋
      </div>
      <p style="font-size:13px;color:#4b5563;line-height:1.6;margin:0 0 20px;">
        El administrador ha registrado a <strong>{nombre_institucion}</strong> en el
        sistema de transporte escolar SafeRoute. A continuación encontrará las
        credenciales de acceso para su cuenta institucional.
      </p>

      <!-- Chip institución -->
      <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:20px;">
        <div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">
          Institución registrada
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
          <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#1d4ed8);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:white;flex-shrink:0;">
            {iniciales}
          </div>
          <div>
            <div style="font-size:13px;font-weight:600;color:#1f2937;">{nombre_institucion}</div>
            <div style="font-size:11px;color:#6b7280;">Institución educativa · SafeRoute</div>
          </div>
        </div>
      </div>

      <!-- Credenciales -->
      <div style="font-size:10px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">
        Credenciales de acceso
      </div>

      <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:16px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
          <span style="font-size:18px;">👤</span>
          <div>
            <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">Usuario</div>
            <div style="font-size:15px;font-weight:700;color:#1f2937;letter-spacing:0.03em;">{user_name}</div>
          </div>
        </div>
        <div style="border-top:1px solid #e2e8f0;margin-bottom:12px;"></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:18px;">🔑</span>
          <div>
            <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">Contraseña temporal</div>
            <div style="font-size:15px;font-weight:700;color:#1f2937;letter-spacing:0.05em;font-family:monospace;">{password_plano}</div>
          </div>
        </div>
      </div>

      <!-- Botón CTA -->
      <div style="text-align:center;margin:24px 0 20px;">
        <a href="{dominio}/login/"
           style="display:inline-block;background:linear-gradient(135deg,#3b82f6,#1d4ed8);color:white;font-weight:700;font-size:14px;padding:14px 36px;border-radius:8px;text-decoration:none;">
          🔓 &nbsp; Iniciar Sesión
        </a>
      </div>

      <!-- Advertencia seguridad -->
      <div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;padding:12px 14px;font-size:11px;color:#92400e;line-height:1.6;margin-bottom:16px;">
        <strong>🔒 Por seguridad:</strong> cambie la contraseña en su primer inicio de sesión.
        No comparta estas credenciales con personas no autorizadas.
      </div>

      <!-- Lo que puede hacer -->
      <div style="font-size:10px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">
        Con su cuenta podrá:
      </div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;">
        <span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Registrar y gestionar estudiantes
      </div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;">
        <span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Administrar rutas y conductores
      </div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;">
        <span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Monitorear el transporte en tiempo real
      </div>
      <div style="font-size:12px;color:#4b5563;padding:4px 0;">
        <span style="color:#3b82f6;font-weight:700;">✓</span> &nbsp;Gestionar pagos y reportes
      </div>

    </div>

    <!-- SECCIÓN DE SEGURIDAD -->
    <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:14px 28px;text-align:center;font-size:11px;color:#6b7280;line-height:1.6;">
      🔒 <strong style="color:#374151;">Correo confidencial.</strong><br>
      Si recibió este correo por error, ignórelo y comuníquese con el administrador.
    </div>

    <!-- PIE DE PÁGINA -->
    <div style="background:#1e293b;border-radius:0 0 12px 12px;padding:20px;text-align:center;">
      <div style="font-size:14px;font-weight:800;color:white;">🚌 SafeRoute</div>
      <div style="font-size:10px;color:#64748b;margin-top:8px;line-height:1.7;">
        Sistema de Gestión de Transporte Escolar<br>
        Bogotá D.C. · Colombia · © 2026 SafeRoute<br>
        Correo enviado a <span style="color:#94a3b8;">{email_destino}</span>
      </div>
    </div>

  </div>
</body>
</html>"""

        correo = EmailMultiAlternatives(
            subject=asunto,
            body=texto_plano,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[email_destino],
        )
        correo.attach_alternative(html, 'text/html')
        correo.send(fail_silently=False)
        print(f'✅ Correo bienvenida enviado a {email_destino}')
        return True

    except Exception as e:
        print(f'[EMAIL ERROR] bienvenida: {e}')
        return False


def _enviar_correo_nueva_password(nombre_institucion, nombre_rector,
                                   email_destino, user_name, password_plano, dominio):
    try:
        asunto = '🔑 SafeRoute — Tu contraseña fue actualizada'

        texto_plano = (
            f'Estimado/a {nombre_rector},\n\n'
            f'El administrador actualizó la contraseña de {nombre_institucion}.\n\n'
            f'  Usuario:    {user_name}\n'
            f'  Contraseña: {password_plano}\n'
            f'  Acceso:     {dominio}/login/\n\n'
            f'— Equipo SafeRoute'
        )

        iniciales = ''.join(p[0].upper() for p in nombre_institucion.split()[:2]) or 'SR'

        html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f6f8fc;font-family:Arial,sans-serif;">
  <div style="max-width:520px;margin:32px auto;">

    <!-- ENCABEZADO -->
    <div style="background:linear-gradient(135deg,#1e293b,#334155);border-radius:12px 12px 0 0;padding:28px;text-align:center;">
      <div style="font-size:36px;">🔑</div>
      <div style="font-size:20px;font-weight:800;color:white;margin-top:8px;">SafeRoute</div>
      <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;">
        Sistema de Gestión de Transporte Escolar
      </div>
      <div style="margin-top:20px;font-size:18px;font-weight:700;color:white;">
        Contraseña actualizada
      </div>
      <div style="font-size:12px;color:#94a3b8;margin-top:4px;">
        El administrador actualizó las credenciales de tu institución
      </div>
    </div>

    <!-- CUERPO -->
    <div style="background:white;padding:28px;">

      <!-- Saludo -->
      <div style="font-size:16px;font-weight:700;color:#1f2937;margin-bottom:8px;">
        Estimado/a <span style="color:#f59e0b;">{nombre_rector}</span> 👋
      </div>
      <p style="font-size:13px;color:#4b5563;line-height:1.6;margin:0 0 20px;">
        El administrador de SafeRoute ha actualizado la contraseña de acceso de
        <strong>{nombre_institucion}</strong>. A continuación encontrará las nuevas
        credenciales.
      </p>

      <!-- Chip institución -->
      <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:14px;margin-bottom:20px;">
        <div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:10px;">
          Institución
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
          <div style="width:38px;height:38px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#1d4ed8);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:white;flex-shrink:0;">
            {iniciales}
          </div>
          <div>
            <div style="font-size:13px;font-weight:600;color:#1f2937;">{nombre_institucion}</div>
            <div style="font-size:11px;color:#6b7280;">Institución educativa · SafeRoute</div>
          </div>
        </div>
      </div>

      <!-- Nuevas credenciales -->
      <div style="font-size:10px;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">
        Nuevas credenciales de acceso
      </div>

      <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:16px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
          <span style="font-size:18px;">👤</span>
          <div>
            <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">Usuario</div>
            <div style="font-size:15px;font-weight:700;color:#1f2937;letter-spacing:0.03em;">{user_name}</div>
          </div>
        </div>
        <div style="border-top:1px solid #e2e8f0;margin-bottom:12px;"></div>
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="font-size:18px;">🔑</span>
          <div>
            <div style="font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;">Nueva contraseña</div>
            <div style="font-size:15px;font-weight:700;color:#1f2937;letter-spacing:0.05em;font-family:monospace;">{password_plano}</div>
          </div>
        </div>
      </div>

      <!-- Botón CTA -->
      <div style="text-align:center;margin:24px 0 20px;">
        <a href="{dominio}/login/"
           style="display:inline-block;background:linear-gradient(135deg,#3b82f6,#1d4ed8);color:white;font-weight:700;font-size:14px;padding:14px 36px;border-radius:8px;text-decoration:none;">
          🔓 &nbsp; Iniciar Sesión
        </a>
      </div>

      <!-- Advertencia seguridad -->
      <div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;padding:12px 14px;font-size:11px;color:#92400e;line-height:1.6;">
        <strong>🔒 Por seguridad:</strong> cambie esta contraseña en su próximo inicio de sesión.
        Si usted no solicitó este cambio, comuníquese con el administrador de inmediato.
      </div>

    </div>

    <!-- SECCIÓN DE SEGURIDAD -->
    <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:14px 28px;text-align:center;font-size:11px;color:#6b7280;line-height:1.6;">
      🔒 <strong style="color:#374151;">Correo confidencial.</strong><br>
      Si recibió este correo por error, ignórelo y comuníquese con el administrador.
    </div>

    <!-- PIE DE PÁGINA -->
    <div style="background:#1e293b;border-radius:0 0 12px 12px;padding:20px;text-align:center;">
      <div style="font-size:14px;font-weight:800;color:white;">🚌 SafeRoute</div>
      <div style="font-size:10px;color:#64748b;margin-top:8px;line-height:1.7;">
        Sistema de Gestión de Transporte Escolar<br>
        Bogotá D.C. · Colombia · © 2026 SafeRoute<br>
        Correo enviado a <span style="color:#94a3b8;">{email_destino}</span>
      </div>
    </div>

  </div>
</body>
</html>"""

        correo = EmailMultiAlternatives(
            subject=asunto,
            body=texto_plano,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=[email_destino],
        )
        correo.attach_alternative(html, 'text/html')
        correo.send(fail_silently=False)
        print(f'✅ Correo nueva contraseña enviado a {email_destino}')
        return True

    except Exception as e:
        print(f'[EMAIL ERROR] nueva password: {e}')
        return False


# ============================================================
# LISTAR COLEGIOS
# ============================================================
def lista_colegios(request):
    if not _solo_admin(request):
        return redirect('login')

    try:
        from .models import Colegio
        busqueda = request.GET.get('busqueda', '')
        estado   = request.GET.get('estado', '')
        tipo     = request.GET.get('tipo', '')
        plan     = request.GET.get('plan', '')

        colegios = Colegio.objects.all().order_by('nombre_institucion')

        if busqueda:
            colegios = colegios.filter(nombre_institucion__icontains=busqueda)
        if estado == 'activo':
            colegios = colegios.filter(activo=True)
        elif estado == 'inactivo':
            colegios = colegios.filter(activo=False)
        if tipo:
            colegios = colegios.filter(tipo_institucion=tipo)
        if plan:
            colegios = colegios.filter(plan=plan)

        context = {
            'colegios':         colegios,
            'total_colegios':   Colegio.objects.count(),
            'colegios_activos': Colegio.objects.filter(activo=True).count(),
            'usuario_nombre':   request.session.get('usuario_nombre'),
            'usuario_rol':      request.session.get('usuario_rol'),
            'busqueda':         busqueda,
            'estado':           estado,
            'tipo':             tipo,
            'plan':             plan,
            'fecha_actual':     date.today(),
        }
    except Exception as e:
        context = {
            'colegios':       [],
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol':    request.session.get('usuario_rol'),
            'error':          f'Error al cargar colegios: {str(e)}',
            'fecha_actual':   date.today(),
        }

    return render(request, 'colegios/lista_colegios.html', context)


# ============================================================
# CREAR COLEGIO
# ============================================================
def nuevo_colegio(request):
    if not _solo_admin(request):
        return redirect('login')

    if request.method == 'POST':
        try:
            from .models import Colegio

            nit                 = request.POST.get('nit', '').strip()
            nombre_institucion  = request.POST.get('nombre_institucion', '').strip()
            tipo_institucion    = request.POST.get('tipo_institucion', '').strip()
            codigo_dane         = request.POST.get('codigo_dane', '').strip() or None
            direccion           = request.POST.get('direccion', '').strip()
            ciudad              = request.POST.get('ciudad', '').strip()
            departamento        = request.POST.get('departamento', '').strip() or None
            telefono            = request.POST.get('telefono', '').strip()
            email_institucional = request.POST.get('email_institucional', '').strip().lower()
            sitio_web           = request.POST.get('sitio_web', '').strip() or None
            nombre_rector       = request.POST.get('nombre_rector', '').strip()
            telefono_rector     = request.POST.get('telefono_rector', '').strip() or None
            email_rector        = request.POST.get('email_rector', '').strip().lower() or None
            max_rutas           = int(request.POST.get('max_rutas', 10))
            max_conductores     = int(request.POST.get('max_conductores', 20))
            max_estudiantes     = int(request.POST.get('max_estudiantes', 500))
            plan                = request.POST.get('plan', 'BASICO')
            observaciones       = request.POST.get('observaciones', '').strip() or None
            activo_val          = request.POST.get('activo', 'true') == 'true'
            user_name           = request.POST.get('user_name', '').strip()
            password            = request.POST.get('password', '').strip()

            ctx = _ctx_nuevo_previo(request, request.POST)

            # ── Validaciones ──────────────────────────────────
            if not nit:
                messages.error(request, 'El NIT es obligatorio.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            if not user_name:
                messages.error(request, 'El nombre de usuario es obligatorio.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            if len(password) < 6:
                messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            if Colegio.objects.filter(nit=nit).exists():
                messages.error(request, 'Ya existe un colegio con ese NIT.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            if Usuario.objects.filter(user_name=user_name).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            if Usuario.objects.filter(cedula=nit).exists():
                messages.error(request, 'Ya existe un usuario con ese NIT.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            if Colegio.objects.filter(email_institucional=email_institucional).exists():
                messages.error(request, 'El email institucional ya está registrado.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            if Usuario.objects.filter(email=email_institucional).exists():
                messages.error(request, 'El email ya está en uso por otro usuario.')
                return render(request, 'colegios/nuevo_colegio.html', ctx)

            # ── Crear usuario de acceso ───────────────────────
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            usuario_colegio = Usuario.objects.create(
                cedula         = nit,
                tipo_documento = 'NIT',
                user_name      = user_name,
                password       = password_hash,
                nombre         = nombre_institucion,
                email          = email_institucional,
                telefono       = telefono or None,
                rol            = 'COLEGIO',
                activo         = activo_val,
            )

            # ── Crear el colegio ──────────────────────────────
            Colegio.objects.create(
                nit                 = nit,
                nombre_institucion  = nombre_institucion,
                tipo_institucion    = tipo_institucion,
                codigo_dane         = codigo_dane,
                logo                = request.FILES.get('logo'),
                direccion           = direccion,
                ciudad              = ciudad,
                departamento        = departamento,
                telefono            = telefono,
                email_institucional = email_institucional,
                sitio_web           = sitio_web,
                nombre_rector       = nombre_rector,
                telefono_rector     = telefono_rector,
                email_rector        = email_rector,
                max_rutas           = max_rutas,
                max_conductores     = max_conductores,
                max_estudiantes     = max_estudiantes,
                plan                = plan,
                observaciones       = observaciones,
                activo              = activo_val,
                usuario             = usuario_colegio,
            )

            # ── Correo de bienvenida ──────────────────────────
            dominio   = request.build_absolute_uri('/')[:-1]
            correo_ok = _enviar_correo_bienvenida_colegio(
                nombre_institucion, nombre_rector,
                email_institucional, user_name, password, dominio,
            )

            if correo_ok:
                messages.success(
                    request,
                    f'✅ Colegio "{nombre_institucion}" registrado. '
                    f'Credenciales enviadas a {email_institucional}.'
                )
            else:
                messages.warning(
                    request,
                    f'✅ Colegio "{nombre_institucion}" registrado, pero no se pudo '
                    f'enviar el correo. Comparte las credenciales manualmente.'
                )

            return redirect('colegios')

        except Exception as e:
            messages.error(request, f'Error al registrar el colegio: {str(e)}')
            return render(request, 'colegios/nuevo_colegio.html',
                          _ctx_nuevo_previo(request, request.POST))

    # ── GET ──────────────────────────────────────────────────
    return render(request, 'colegios/nuevo_colegio.html', _ctx_nuevo_vacio(request))


# ============================================================
# EDITAR COLEGIO
# ============================================================
def editar_colegio(request, nit):
    if not _solo_admin(request):
        return redirect('login')

    try:
        from .models import Colegio
        colegio = Colegio.objects.get(nit=nit)
    except Exception:
        messages.error(request, 'Colegio no encontrado.')
        return redirect('colegios')

    if request.method == 'POST':
        try:
            colegio.nombre_institucion  = request.POST.get('nombre_institucion', '').strip()
            colegio.tipo_institucion    = request.POST.get('tipo_institucion', '').strip()
            colegio.codigo_dane         = request.POST.get('codigo_dane', '').strip() or None
            colegio.direccion           = request.POST.get('direccion', '').strip()
            colegio.ciudad              = request.POST.get('ciudad', '').strip()
            colegio.departamento        = request.POST.get('departamento', '').strip() or None
            colegio.telefono            = request.POST.get('telefono', '').strip()
            colegio.email_institucional = request.POST.get('email_institucional', '').strip().lower()
            colegio.sitio_web           = request.POST.get('sitio_web', '').strip() or None
            colegio.nombre_rector       = request.POST.get('nombre_rector', '').strip()
            colegio.telefono_rector     = request.POST.get('telefono_rector', '').strip() or None
            colegio.email_rector        = request.POST.get('email_rector', '').strip().lower() or None
            colegio.max_rutas           = int(request.POST.get('max_rutas', 10))
            colegio.max_conductores     = int(request.POST.get('max_conductores', 20))
            colegio.max_estudiantes     = int(request.POST.get('max_estudiantes', 500))
            colegio.plan                = request.POST.get('plan', 'BASICO')
            colegio.observaciones = request.POST.get('observaciones', '').strip() or None
            activo_val = request.POST.get('activo', 'true') == 'true'
            colegio.activo = activo_val
            logo_nuevo = request.FILES.get('logo')
            if logo_nuevo:
                colegio.logo = logo_nuevo         
            colegio.save()

            password_nueva = request.POST.get('password', '').strip()
            correo_enviado = False

            if colegio.usuario:
                colegio.usuario.nombre   = colegio.nombre_institucion
                colegio.usuario.email    = colegio.email_institucional
                colegio.usuario.telefono = colegio.telefono or None
                colegio.usuario.activo   = activo_val

                if password_nueva:
                    colegio.usuario.password = bcrypt.hashpw(
                        password_nueva.encode(), bcrypt.gensalt()
                    ).decode()
                    colegio.usuario.save()
                    dominio = request.build_absolute_uri('/')[:-1]
                    correo_enviado = _enviar_correo_nueva_password(
                        colegio.nombre_institucion, colegio.nombre_rector,
                        colegio.email_institucional, colegio.usuario.user_name,
                        password_nueva, dominio,
                    )
                else:
                    colegio.usuario.save()

            if password_nueva:
                if correo_enviado:
                    messages.success(
                        request,
                        f'✅ Colegio actualizado. Nueva contraseña enviada a {colegio.email_institucional}.'
                    )
                else:
                    messages.warning(
                        request,
                        f'✅ Colegio actualizado, pero no se pudo enviar el correo. '
                        f'Notifique la nueva contraseña manualmente.'
                    )
            else:
                messages.success(request, f'✅ Colegio "{colegio.nombre_institucion}" actualizado.')

            return redirect('colegios')

        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')

    # ── GET editar ────────────────────────────────────────────
    return render(request, 'colegios/nuevo_colegio.html', _ctx_editar(request, colegio))


# ============================================================
# ELIMINAR COLEGIO
# ============================================================
def eliminar_colegio(request, nit):
    if not _solo_admin(request):
        return redirect('login')

    try:
        from .models import Colegio
        colegio = Colegio.objects.get(nit=nit)
        nombre  = colegio.nombre_institucion
        if colegio.usuario:
            colegio.usuario.delete()
        else:
            colegio.delete()
        messages.success(request, f'Colegio "{nombre}" eliminado permanentemente.')
    except Colegio.DoesNotExist:
        messages.error(request, 'Colegio no encontrado.')
    except Exception as e:
        messages.error(request, f'Error al eliminar: {str(e)}')

    return redirect('colegios')