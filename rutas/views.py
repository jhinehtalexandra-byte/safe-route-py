# rutas/views.py  — corregido para usar db_column correctos
import json
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import Ruta, Parada, Recorrido, ParadaRecorrido


# ============================================================
# HELPERS
# ============================================================
def _sesion_activa(request):
    return bool(request.session.get('usuario_cedula'))


def _rol_en(request, *roles):
    rol = request.session.get('usuario_rol')
    if rol == 'ADMIN':
        return True
    return rol in roles


def _ctx_base(request):
    """Contexto mínimo siempre presente para que los templates no fallen."""
    return {
        'usuario_nombre':      request.session.get('usuario_nombre'),
        'usuario_rol':         request.session.get('usuario_rol'),
        'fecha_actual':        date.today(),
        'paradas_completadas': [],
        'paradas_pendientes':  [],
        'parada_actual_rec':   None,
        'lista_confirmada':    False,
        'paradas_mapa_json':   '[]',
        'proxima_parada_json': 'null',
        'ubicacion_lat':       None,
        'ubicacion_lng':       None,
        'ruta_actual':         None,
        'recorrido':           None,
    }


# ============================================================
# LISTA DE RUTAS
# ============================================================
def lista_rutas(request):
    if not _sesion_activa(request):
        return redirect('login')

    try:
        busqueda = request.GET.get('busqueda', '')
        turno    = request.GET.get('turno', '')
        estado   = request.GET.get('estado', '')

        rutas = Ruta.objects.all().order_by('nombre')
        if busqueda:
            rutas = rutas.filter(nombre__icontains=busqueda)
        if turno:
            rutas = rutas.filter(turno=turno)
        if estado == 'activo':
            rutas = rutas.filter(activo=True)
        elif estado == 'inactivo':
            rutas = rutas.filter(activo=False)

        context = {
            'rutas':          rutas,
            'total_rutas':    Ruta.objects.count(),
            'rutas_activas':  Ruta.objects.filter(activo=True).count(),
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol':    request.session.get('usuario_rol'),
            'busqueda':       busqueda,
            'turno':          turno,
            'estado':         estado,
            'fecha_actual':   date.today(),
        }
    except Exception as e:
        context = {
            'rutas':          [],
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol':    request.session.get('usuario_rol'),
            'error':          f'Error al cargar rutas: {str(e)}',
            'fecha_actual':   date.today(),
        }

    return render(request, 'rutas/lista_rutas.html', context)


# ============================================================
# GESTIÓN DE RUTAS (Colegio: crear y asignar rutas)
# ============================================================
def gestion_rutas(request):
    if not _sesion_activa(request):
        return redirect('login')
    if not _rol_en(request, 'COLEGIO', 'ADMIN'):
        return redirect('login')

    try:
        from usuarios.models import Usuario
        from monitoras.models import Monitora

        # Filtros GET para búsqueda
        busqueda = request.GET.get('busqueda', '').strip()
        turno    = request.GET.get('turno', '').strip()

        conductores = Usuario.objects.filter(rol='CONDUCTOR', activo=True)
        monitoras   = Monitora.objects.filter(usuario__activo=True).select_related('usuario')

        if request.method == 'POST':
            accion = request.POST.get('accion', '')

            if accion == 'crear':
                codigo        = request.POST.get('codigo', '').strip()
                nombre        = request.POST.get('nombre', '').strip()
                descripcion   = request.POST.get('descripcion', '').strip()
                turno_post    = request.POST.get('turno', '').strip()
                hora_inicio   = request.POST.get('hora_inicio', '').strip() or None
                hora_fin      = request.POST.get('hora_fin', '').strip() or None
                capacidad     = request.POST.get('capacidad_maxima', '').strip() or None
                conductor_ced = request.POST.get('conductor_cedula', '').strip() or None

                if Ruta.objects.filter(codigo=codigo).exists():
                    messages.error(request, 'Ya existe una ruta con ese código.')
                else:
                    conductor_obj = None
                    if conductor_ced:
                        conductor_obj = Usuario.objects.filter(cedula=conductor_ced).first()

                    Ruta.objects.create(
                        codigo           = codigo,
                        nombre           = nombre,
                        descripcion      = descripcion or None,
                        turno            = turno_post or None,
                        hora_inicio      = hora_inicio,
                        hora_fin         = hora_fin,
                        capacidad_maxima = int(capacidad) if capacidad else None,
                        conductor_cedula = conductor_obj,
                        activo           = True,
                    )
                    messages.success(request, f'✅ Ruta "{nombre}" creada exitosamente.')
                return redirect('rutas_gestion')

            elif accion == 'editar':
                codigo        = request.POST.get('codigo', '').strip()
                turno_post    = request.POST.get('turno', '').strip()
                conductor_ced = request.POST.get('conductor_cedula', '').strip() or None
                monitora_ced  = request.POST.get('monitora_cedula', '').strip() or None
                try:
                    from monitoras.models import Monitora
                    ruta              = Ruta.objects.get(codigo=codigo)
                    ruta.nombre       = request.POST.get('nombre', ruta.nombre).strip()
                    ruta.descripcion  = request.POST.get('descripcion', '').strip() or None
                    ruta.turno        = turno_post or None
                    hora_inicio       = request.POST.get('hora_inicio', '').strip()
                    hora_fin          = request.POST.get('hora_fin', '').strip()
                    ruta.hora_inicio  = hora_inicio or None
                    ruta.hora_fin     = hora_fin or None
                    capacidad         = request.POST.get('capacidad_maxima', '').strip()
                    ruta.capacidad_maxima = int(capacidad) if capacidad else None
                    ruta.activo       = request.POST.get('activo') == 'on'
                    ruta.conductor_cedula = Usuario.objects.filter(cedula=conductor_ced).first() if conductor_ced else None
                    ruta.save()

                    # Desasignar monitora anterior de esta ruta
                    Monitora.objects.filter(ruta_asignada=ruta).update(ruta_asignada=None)

                    # Asignar nueva monitora si se seleccionó
                    if monitora_ced:
                        Monitora.objects.filter(
                            usuario__cedula=monitora_ced
                        ).update(ruta_asignada=ruta)

                    messages.success(request, f'✅ Ruta "{ruta.nombre}" actualizada.')
                except Ruta.DoesNotExist:
                    messages.error(request, 'Ruta no encontrada.')
                return redirect('rutas_gestion')

            elif accion == 'eliminar':
                codigo = request.POST.get('codigo', '').strip()
                try:
                    ruta   = Ruta.objects.get(codigo=codigo)
                    nombre = ruta.nombre
                    ruta.delete()
                    messages.success(request, f'Ruta "{nombre}" eliminada.')
                except Ruta.DoesNotExist:
                    messages.error(request, 'Ruta no encontrada.')
                return redirect('rutas_gestion')

            elif accion == 'parada_nueva':
                codigo_ruta = request.POST.get('codigo_ruta', '').strip()
                try:
                    ruta        = Ruta.objects.get(codigo=codigo_ruta)
                    ultimo_orden = Parada.objects.filter(ruta=ruta).count()
                    Parada.objects.create(
                        ruta       = ruta,
                        orden      = ultimo_orden + 1,
                        nombre     = request.POST.get('parada_nombre', '').strip(),
                        direccion  = request.POST.get('parada_direccion', '').strip(),
                        referencia = request.POST.get('parada_referencia', '').strip() or None,
                        latitud    = request.POST.get('parada_lat', '').strip() or None,
                        longitud   = request.POST.get('parada_lng', '').strip() or None,
                        activo     = True,
                    )
                    messages.success(request, 'Parada agregada correctamente.')
                except Ruta.DoesNotExist:
                    messages.error(request, 'Ruta no encontrada.')
                return redirect('rutas_gestion')

            elif accion == 'parada_eliminar':
                parada_id = request.POST.get('parada_id', '').strip()
                try:
                    parada = Parada.objects.get(id=parada_id)
                    parada.delete()
                    messages.success(request, 'Parada eliminada.')
                except Parada.DoesNotExist:
                    messages.error(request, 'Parada no encontrada.')
                return redirect('rutas_gestion')

        # GET — aplicar filtros de búsqueda
        rutas = Ruta.objects.prefetch_related('paradas').order_by('nombre')
        if busqueda:
            rutas = rutas.filter(nombre__icontains=busqueda)
        if turno:
            rutas = rutas.filter(turno=turno)

        context = {
            'rutas':          rutas,
            'conductores':    conductores,
            'monitoras':      monitoras,
            'turnos':         Ruta.TURNO,
            'total_rutas':    Ruta.objects.count(),
            'rutas_activas':  Ruta.objects.filter(activo=True).count(),
            'busqueda':       busqueda,
            'turno':          turno,
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol':    request.session.get('usuario_rol'),
            'fecha_actual':   date.today(),
        }

    except Exception as e:
        context = {
            'rutas':          [],
            'conductores':    [],
            'monitoras':      [],
            'turnos':         [],
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol':    request.session.get('usuario_rol'),
            'error':          f'Error: {str(e)}',
            'fecha_actual':   date.today(),
        }

    return render(request, 'rutas/gestion_rutas.html', context)


# ============================================================
# MAPA EN TIEMPO REAL (Admin / Colegio / Padre)
# ============================================================
def mapa_tiempo_real(request):
    if not _sesion_activa(request):
        return redirect('login')
    if not _rol_en(request, 'ADMIN', 'COLEGIO', 'PADRE'):
        return redirect('login')

    try:
        rol    = request.session.get('usuario_rol')
        cedula = request.session.get('usuario_cedula')

        if rol in ('ADMIN', 'COLEGIO'):
            ruta_id    = request.GET.get('ruta', '')
            # Usar el campo correcto: db_column='ruta' → acceder por ruta
            recorridos = Recorrido.objects.filter(
                fecha=date.today(), estado='EN_CURSO'
            ).select_related('ruta', 'conductor')
            if ruta_id:
                recorridos = recorridos.filter(ruta__codigo=ruta_id)
            recorrido     = recorridos.first()
            rutas_activas = Ruta.objects.filter(activo=True)
        else:
            from estudiantes.models import Estudiante
            hijo = Estudiante.objects.filter(
                cedula_padre=cedula, activo=True
            ).select_related('codigo_ruta').first()
            recorrido     = None
            rutas_activas = []
            if hijo and hijo.codigo_ruta:
                recorrido = Recorrido.objects.filter(
                    ruta=hijo.codigo_ruta,
                    fecha=date.today(),
                    estado='EN_CURSO',
                ).first()

        context = {
            'recorrido':      recorrido,
            'rutas_activas':  rutas_activas if rol in ('ADMIN', 'COLEGIO') else [],
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol':    rol,
            'fecha_actual':   date.today(),
        }
    except Exception as e:
        context = {
            'error':          f'Error al cargar monitoreo: {str(e)}',
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol':    request.session.get('usuario_rol'),
            'fecha_actual':   date.today(),
            'recorrido':      None,
            'rutas_activas':  [],
        }

    return render(request, 'rutas/mapa_tiempo_real.html', context)


# ============================================================
# MAPA CONDUCTOR  (6.5)
# ============================================================
def mapa_conductor(request):
    if not _sesion_activa(request):
        return redirect('login')
    if not _rol_en(request, 'CONDUCTOR'):
        return redirect('login')

    ctx = _ctx_base(request)

    try:
        cedula = request.session.get('usuario_cedula')

        # Buscar recorrido del día — usar campo 'conductor' (db_column)
        recorrido = Recorrido.objects.filter(
            conductor__cedula=cedula,
            fecha=date.today(),
        ).exclude(estado='CANCELADO').order_by('-fecha_creacion').first()

        ruta_actual         = None
        paradas_completadas = []
        paradas_pendientes  = []

        if recorrido:
            ruta_actual       = recorrido.ruta
            paradas_qs        = (
                ParadaRecorrido.objects
                .filter(recorrido=recorrido)
                .select_related('parada')
                .order_by('parada__orden')
            )
            paradas_completadas = [p for p in paradas_qs if p.estado == 'COMPLETADA']
            paradas_pendientes  = [p for p in paradas_qs if p.estado == 'PENDIENTE']
        else:
            from usuarios.models import Usuario
            conductor_obj = Usuario.objects.filter(cedula=cedula).first()
            if conductor_obj:
                ruta_actual = Ruta.objects.filter(
                    conductor_cedula=conductor_obj, activo=True
                ).first()

        parada_actual_rec = paradas_pendientes[0] if paradas_pendientes else None

        lista_confirmada = (
            request.session.get('lista_confirmada', False) or
            (recorrido and recorrido.lista_confirmada)
        )

        paradas_mapa = []
        if ruta_actual:
            paradas_mapa = list(
                Parada.objects.filter(ruta=ruta_actual, activo=True)
                .order_by('orden')
                .values('id', 'orden', 'nombre', 'direccion', 'latitud', 'longitud')
            )

        proxima = paradas_pendientes[0].parada if paradas_pendientes else None

        ctx.update({
            'ruta_actual':         ruta_actual,
            'recorrido':           recorrido,
            'paradas_completadas': paradas_completadas,
            'paradas_pendientes':  paradas_pendientes,
            'parada_actual_rec':   parada_actual_rec,
            'lista_confirmada':    lista_confirmada,
            'paradas_mapa_json':   json.dumps(paradas_mapa, default=str),
            'proxima_parada_json': json.dumps(
                {'id': proxima.id, 'nombre': proxima.nombre, 'direccion': proxima.direccion}
                if proxima else None
            ),
            'ubicacion_lat': float(recorrido.ubicacion_lat) if recorrido and recorrido.ubicacion_lat else None,
            'ubicacion_lng': float(recorrido.ubicacion_lng) if recorrido and recorrido.ubicacion_lng else None,
        })

    except Exception as e:
        ctx['error'] = f'Error al cargar el mapa: {str(e)}'

    return render(request, 'rutas/mapa/mapa_conductor.html', ctx)


# ============================================================
# INICIAR RECORRIDO
# ============================================================
@require_POST
def iniciar_recorrido(request):
    if not _sesion_activa(request):
        return JsonResponse({'ok': False, 'error': 'Sin sesión'}, status=403)

    try:
        data     = json.loads(request.body)
        ruta_id  = data.get('ruta_codigo')
        lista_ok = (
            request.session.get('lista_confirmada', False) or
            data.get('lista_confirmada', False)
        )

        if not lista_ok:
            return JsonResponse({'ok': False, 'error': 'La monitora aún no ha confirmado la lista.'}, status=400)

        cedula = request.session.get('usuario_cedula')
        from usuarios.models import Usuario
        conductor = Usuario.objects.get(cedula=cedula)
        ruta      = Ruta.objects.get(codigo=ruta_id)

        recorrido, creado = Recorrido.objects.get_or_create(
            ruta      = ruta,
            conductor = conductor,
            fecha     = date.today(),
            defaults  = {
                'estado':           'EN_CURSO',
                'hora_inicio_real': datetime.now(),
                'lista_confirmada': True,
            }
        )

        if not creado:
            recorrido.estado           = 'EN_CURSO'
            recorrido.hora_inicio_real = recorrido.hora_inicio_real or datetime.now()
            recorrido.lista_confirmada = True
            recorrido.save()

        paradas = Parada.objects.filter(ruta=ruta, activo=True).order_by('orden')
        for parada in paradas:
            ParadaRecorrido.objects.get_or_create(
                recorrido=recorrido,
                parada=parada,
                defaults={'estado': 'PENDIENTE'}
            )

        return JsonResponse({'ok': True, 'recorrido_id': recorrido.id, 'mensaje': '¡Recorrido iniciado!'})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ============================================================
# NOTIFICAR LLEGADA A PARADA
# ============================================================
@require_POST
def notificar_llegada(request):
    if not _sesion_activa(request):
        return JsonResponse({'ok': False, 'error': 'Sin sesión'}, status=403)

    try:
        data         = json.loads(request.body)
        recorrido_id = data.get('recorrido_id')
        parada_id    = data.get('parada_id')

        parada_rec              = get_object_or_404(ParadaRecorrido, recorrido_id=recorrido_id, parada_id=parada_id)
        parada_rec.estado       = 'COMPLETADA'
        parada_rec.hora_llegada = datetime.now()
        parada_rec.observacion  = data.get('observacion') or None
        parada_rec.save()

        _notificar_acudientes_llegada(parada_rec)

        siguiente = (
            ParadaRecorrido.objects
            .filter(recorrido_id=recorrido_id, estado='PENDIENTE')
            .order_by('parada__orden')
            .first()
        )

        return JsonResponse({
            'ok':            True,
            'completadas':   ParadaRecorrido.objects.filter(recorrido_id=recorrido_id, estado='COMPLETADA').count(),
            'pendientes':    ParadaRecorrido.objects.filter(recorrido_id=recorrido_id, estado='PENDIENTE').count(),
            'siguiente_id':  siguiente.parada_id    if siguiente else None,
            'siguiente_nom': siguiente.parada.nombre if siguiente else None,
        })

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ============================================================
# FINALIZAR RECORRIDO
# ============================================================
@require_POST
def finalizar_recorrido(request):
    if not _sesion_activa(request):
        return JsonResponse({'ok': False, 'error': 'Sin sesión'}, status=403)

    try:
        data         = json.loads(request.body)
        recorrido_id = data.get('recorrido_id')

        recorrido               = get_object_or_404(Recorrido, id=recorrido_id)
        recorrido.estado        = 'FINALIZADO'
        recorrido.hora_fin_real = datetime.now()
        recorrido.ubicacion_lat = None
        recorrido.ubicacion_lng = None
        recorrido.save()

        ParadaRecorrido.objects.filter(recorrido=recorrido, estado='PENDIENTE').update(estado='SALTADA')

        return JsonResponse({'ok': True, 'mensaje': 'Recorrido finalizado correctamente.'})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ============================================================
# ACTUALIZAR UBICACIÓN DEL CONDUCTOR
# ============================================================
@require_POST
@csrf_exempt
def actualizar_ubicacion(request):
    if not _sesion_activa(request):
        return JsonResponse({'ok': False}, status=403)

    try:
        data         = json.loads(request.body)
        recorrido_id = data.get('recorrido_id')
        lat          = data.get('lat')
        lng          = data.get('lng')

        if not all([recorrido_id, lat, lng]):
            return JsonResponse({'ok': False, 'error': 'Datos incompletos'}, status=400)

        Recorrido.objects.filter(id=recorrido_id).update(
            ubicacion_lat                = lat,
            ubicacion_lng                = lng,
            ultima_ubicacion_actualizada = datetime.now(),
        )
        return JsonResponse({'ok': True})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ============================================================
# OBTENER UBICACIÓN (polling padre/admin)
# ============================================================
@require_GET
def obtener_ubicacion(request, recorrido_id):
    if not _sesion_activa(request):
        return JsonResponse({'ok': False}, status=403)

    try:
        rec = get_object_or_404(Recorrido, id=recorrido_id)

        paradas = list(
            ParadaRecorrido.objects
            .filter(recorrido=rec)
            .select_related('parada')
            .order_by('parada__orden')
            .values(
                'parada__id', 'parada__nombre', 'parada__direccion',
                'parada__latitud', 'parada__longitud', 'parada__orden',
                'estado', 'hora_llegada',
            )
        )

        return JsonResponse({
            'ok':          True,
            'estado':      rec.estado,
            'lat':         float(rec.ubicacion_lat) if rec.ubicacion_lat else None,
            'lng':         float(rec.ubicacion_lng) if rec.ubicacion_lng else None,
            'actualizado': rec.ultima_ubicacion_actualizada.isoformat() if rec.ultima_ubicacion_actualizada else None,
            'paradas':     paradas,
        }, default=str)

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)


# ============================================================
# MONITOREO (alias que redirige a mapa_tiempo_real)
# ============================================================
def monitoreo(request):
    return mapa_tiempo_real(request)


# ============================================================
# REGISTRAR CONDUCTOR / MONITORA
# ============================================================
def registrar_conductor_monitora(request):
    if not _sesion_activa(request):
        return redirect('login')
    if not _rol_en(request, 'COLEGIO', 'ADMIN'):
        return redirect('login')
    return redirect('usuarios_nuevo')


# ============================================================
# AUXILIAR — Notificar acudientes al llegar a parada
# ============================================================
def _notificar_acudientes_llegada(parada_rec):
    try:
        from estudiantes.models import EstudianteAcudiente
        from django.core.mail import send_mail
        from django.conf import settings as cfg

        estudiantes = parada_rec.parada.ruta.estudiante_set.filter(activo=True)

        for est in estudiantes:
            vincs = EstudianteAcudiente.objects.filter(estudiante=est).select_related('acudiente')
            for vinc in vincs:
                acudiente = vinc.acudiente
                if not acudiente.email:
                    continue
                try:
                    send_mail(
                        subject=f'🚌 {est.nombre} llegó a la parada — RutaEscolar',
                        message=(
                            f'Hola {acudiente.nombre},\n\n'
                            f'{est.nombre} {est.apellido} fue recogido/a en '
                            f'"{parada_rec.parada.nombre}" a las '
                            f'{parada_rec.hora_llegada.strftime("%H:%M")}.\n\n'
                            f'— Equipo RutaEscolar'
                        ),
                        from_email=getattr(cfg, 'DEFAULT_FROM_EMAIL', 'noreply@rutaescolar.co'),
                        recipient_list=[acudiente.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
    except Exception as e:
        print(f'⚠️ Error notificando acudientes: {e}')
        
@require_POST
def iniciar_recorrido_form(request):
    if not _sesion_activa(request):
        return redirect('login')
    try:
        recorrido_id = request.POST.get('recorrido_id')
        recorrido    = Recorrido.objects.get(id=recorrido_id)
        if not recorrido.lista_confirmada:
            messages.error(request, 'La monitora aun no ha confirmado la lista.')
            return redirect('dashboard_conductor')
        recorrido.estado           = 'EN_CURSO'
        recorrido.hora_inicio_real = recorrido.hora_inicio_real or datetime.now()
        recorrido.save()
        paradas = Parada.objects.filter(ruta=recorrido.ruta, activo=True).order_by('orden')
        for p in paradas:
            ParadaRecorrido.objects.get_or_create(recorrido=recorrido, parada=p, defaults={'estado': 'PENDIENTE'})
        messages.success(request, 'Recorrido iniciado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al iniciar recorrido: {str(e)}')
    return redirect('dashboard_conductor')


@require_POST
def finalizar_recorrido_form(request):
    if not _sesion_activa(request):
        return redirect('login')
    try:
        recorrido_id            = request.POST.get('recorrido_id')
        recorrido               = Recorrido.objects.get(id=recorrido_id)
        recorrido.estado        = 'FINALIZADO'
        recorrido.hora_fin_real = datetime.now()
        recorrido.save()
        ParadaRecorrido.objects.filter(recorrido=recorrido, estado='PENDIENTE').update(estado='SALTADA')
        messages.success(request, 'Recorrido finalizado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al finalizar: {str(e)}')
    return redirect('dashboard_conductor')


@require_POST
def notificar_llegada_form(request):
    if not _sesion_activa(request):
        return redirect('login')
    try:
        pr_id      = request.POST.get('parada_recorrido_id')
        parada_rec = ParadaRecorrido.objects.get(id=pr_id)
        parada_rec.estado       = 'COMPLETADA'
        parada_rec.hora_llegada = datetime.now()
        parada_rec.save()
        _notificar_acudientes_llegada(parada_rec)
        messages.success(request, f'Llegada a "{parada_rec.parada.nombre}" registrada.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('dashboard_conductor')


# ============================================================
# INICIAR RECORRIDO � Form HTML (dashboard conductor)
# ============================================================
from django.views.decorators.http import require_POST as _rp

@_rp
def iniciar_recorrido_form(request):
    if not _sesion_activa(request):
        return redirect('login')
    try:
        recorrido_id = request.POST.get('recorrido_id')
        recorrido    = Recorrido.objects.get(id=recorrido_id)
        if not recorrido.lista_confirmada:
            messages.error(request, 'La monitora aun no ha confirmado la lista.')
            return redirect('dashboard_conductor')
        recorrido.estado           = 'EN_CURSO'
        recorrido.hora_inicio_real = recorrido.hora_inicio_real or datetime.now()
        recorrido.save()
        paradas = Parada.objects.filter(ruta=recorrido.ruta, activo=True).order_by('orden')
        for p in paradas:
            ParadaRecorrido.objects.get_or_create(recorrido=recorrido, parada=p, defaults={'estado': 'PENDIENTE'})
        messages.success(request, 'Recorrido iniciado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al iniciar recorrido: {str(e)}')
    return redirect('dashboard_conductor')


@_rp
def finalizar_recorrido_form(request):
    if not _sesion_activa(request):
        return redirect('login')
    try:
        recorrido_id            = request.POST.get('recorrido_id')
        recorrido               = Recorrido.objects.get(id=recorrido_id)
        recorrido.estado        = 'FINALIZADO'
        recorrido.hora_fin_real = datetime.now()
        recorrido.save()
        ParadaRecorrido.objects.filter(recorrido=recorrido, estado='PENDIENTE').update(estado='SALTADA')
        messages.success(request, 'Recorrido finalizado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al finalizar: {str(e)}')
    return redirect('dashboard_conductor')


@_rp
def notificar_llegada_form(request):
    if not _sesion_activa(request):
        return redirect('login')
    try:
        pr_id      = request.POST.get('parada_recorrido_id')
        parada_rec = ParadaRecorrido.objects.get(id=pr_id)
        parada_rec.estado       = 'COMPLETADA'
        parada_rec.hora_llegada = datetime.now()
        parada_rec.save()
        _notificar_acudientes_llegada(parada_rec)
        messages.success(request, f'Llegada a "{parada_rec.parada.nombre}" registrada.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('dashboard_conductor')
