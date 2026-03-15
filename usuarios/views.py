import bcrypt
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuario


# ============================================
# HOME
# ============================================
def home(request):
    return render(request, 'home.html')


# ============================================
# LOGIN
# ============================================
def login_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        password  = request.POST.get('password')
        try:
            usuario = Usuario.objects.get(user_name=user_name, activo=True)

            # ✅ Verificar contraseña BCrypt
            password_bytes    = password.encode('utf-8')
            hash_bytes        = usuario.password.encode('utf-8')
            password_correcta = bcrypt.checkpw(password_bytes, hash_bytes)

            if password_correcta:
                # Guardar datos del usuario en la sesión
                request.session['usuario_cedula'] = usuario.cedula
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_rol']    = usuario.rol

                # Redirigir según el rol
                if usuario.rol == 'ADMIN':
                    return redirect('dashboard_admin')
                elif usuario.rol == 'CONDUCTOR':
                    return redirect('dashboard_conductor')
                else:
                    return redirect('dashboard_padre')
            else:
                return render(request, 'login.html', {
                    'error': 'Usuario o contraseña incorrectos'
                })

        except Usuario.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request, 'login.html')


# ============================================
# LOGOUT
# ============================================
def logout_view(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')


# ============================================
# CONTACTO
# ============================================
def contacto(request):
    if request.method == 'POST':
        messages.success(request, '¡Mensaje enviado exitosamente!')
    return redirect('home')


# ============================================
# DASHBOARD ADMIN
# ============================================
def dashboard_admin(request):
    # Verificar que el usuario esté logueado y sea ADMIN
    if not request.session.get('usuario_cedula'):
        return redirect('login')
    if request.session.get('usuario_rol') != 'ADMIN':
        return redirect('login')

    from datetime import date
    from estudiantes.models import Estudiante
    from rutas.models import Ruta
    from pagos.models import Pago

    context = {
        'fecha_actual':      date.today(),
        'total_estudiantes': Estudiante.objects.filter(activo=True).count(),
        'total_rutas':       Ruta.objects.filter(activo=True).count(),
        'ingresos_mes':      Pago.objects.filter(estado='PAGADO').count(),
        'pagos_pendientes':  Pago.objects.filter(estado='PENDIENTE').count(),
        'proximas_rutas':    Ruta.objects.filter(activo=True)[:3],
        'usuario_nombre':    request.session.get('usuario_nombre'),
    }
    return render(request, 'dashboard_admin.html', context)


# ============================================
# DASHBOARD CONDUCTOR
# ============================================
def dashboard_conductor(request):
    # Verificar que el usuario esté logueado y sea CONDUCTOR
    if not request.session.get('usuario_cedula'):
        return redirect('login')
    if request.session.get('usuario_rol') != 'CONDUCTOR':
        return redirect('login')

    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
    }
    return render(request, 'dashboard_conductor.html', context)


# ============================================
# DASHBOARD PADRE
# ============================================
def dashboard_padre(request):
    # Verificar que el usuario esté logueado y sea PADRE
    if not request.session.get('usuario_cedula'):
        return redirect('login')
    if request.session.get('usuario_rol') != 'PADRE':
        return redirect('login')

    context = {
        'usuario_nombre': request.session.get('usuario_nombre'),
    }
    return render(request, 'dashboard_padre.html', context)


# ============================================
# REGISTRARSE
# ============================================
def registrarse(request):
    if request.method == 'POST':
        cedula         = request.POST.get('cedula')
        tipo_documento = request.POST.get('tipo_documento')
        user_name      = request.POST.get('user_name')
        password       = request.POST.get('password')
        nombre         = request.POST.get('nombre')
        email          = request.POST.get('email')
        telefono       = request.POST.get('telefono')

        # Verificar si el usuario ya existe
        if Usuario.objects.filter(user_name=user_name).exists():
            return render(request, 'registrarse.html', {
                'error': 'El nombre de usuario ya existe'
            })

        if Usuario.objects.filter(email=email).exists():
            return render(request, 'registrarse.html', {
                'error': 'El email ya está registrado'
            })

        # Encriptar contraseña con BCrypt
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Crear el usuario
        Usuario.objects.create(
            cedula         = cedula,
            tipo_documento = tipo_documento,
            user_name      = user_name,
            password       = password_hash,
            nombre         = nombre,
            email          = email,
            telefono       = telefono,
            rol            = 'PADRE',   # por defecto se registran como padres
            activo         = True
        )

        messages.success(request, 'Registro exitoso. Ya puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'registrarse.html')


# ============================================
# GESTIÓN DE USUARIOS (solo ADMIN)
# ============================================
def usuarios(request):
    if not request.session.get('usuario_cedula'):
        return redirect('login')
    if request.session.get('usuario_rol') != 'ADMIN':
        return redirect('login')

    lista = Usuario.objects.filter(activo=True).order_by('nombre')
    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': lista,
        'usuario_nombre': request.session.get('usuario_nombre'),
    })


def usuarios_nuevo(request):
    if not request.session.get('usuario_cedula'):
        return redirect('login')
    if request.session.get('usuario_rol') != 'ADMIN':
        return redirect('login')

    if request.method == 'POST':
        cedula         = request.POST.get('cedula')
        tipo_documento = request.POST.get('tipo_documento')
        user_name      = request.POST.get('user_name')
        password       = request.POST.get('password')
        nombre         = request.POST.get('nombre')
        email          = request.POST.get('email')
        telefono       = request.POST.get('telefono')
        rol            = request.POST.get('rol')

        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        Usuario.objects.create(
            cedula         = cedula,
            tipo_documento = tipo_documento,
            user_name      = user_name,
            password       = password_hash,
            nombre         = nombre,
            email          = email,
            telefono       = telefono,
            rol            = rol,
            activo         = True
        )
        messages.success(request, 'Usuario creado exitosamente.')
        return redirect('usuarios')

    return render(request, 'usuarios/nuevo_usuario.html', {
        'usuario_nombre': request.session.get('usuario_nombre'),
    })


# ============================================
# PERFIL
# ============================================
def perfil(request):
    if not request.session.get('usuario_cedula'):
        return redirect('login')

    try:
        usuario = Usuario.objects.get(cedula=request.session.get('usuario_cedula'))
    except Usuario.DoesNotExist:
        return redirect('login')

    return render(request, 'perfil.html', {
        'usuario': usuario,
        'usuario_nombre': request.session.get('usuario_nombre'),
    })


# ============================================
# REPORTES (solo ADMIN)
# ============================================
def reportes(request):
    if not request.session.get('usuario_cedula'):
        return redirect('login')
    if request.session.get('usuario_rol') != 'ADMIN':
        return redirect('login')

    return render(request, 'reportes.html', {
        'usuario_nombre': request.session.get('usuario_nombre'),
    })