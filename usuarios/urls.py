# usuarios/urls.py
from django.urls import path
from . import views
from estudiantes  import views as estudiantes_views
from rutas        import views as rutas_views
from pagos        import views as pagos_views
from colegios     import views as colegios_views
from conductores  import views as conductores_views
from monitoras    import views as monitoras_views

urlpatterns = [

    # ── Páginas públicas ─────────────────────────────────────────
    path('',                    views.home,               name='home'),
    path('login/',              views.login_view,         name='login'),
    path('logout/',             views.logout_view,        name='logout'),
    path('registrarse/',        views.registrarse,        name='registrarse'),
    path('contacto/',           views.contacto,           name='contacto'),
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    path('restablecer-password/<str:token>/', views.restablecer_password, name='restablecer_password'),
    path('terminos/',           views.terminos,           name='terminos'),
    path('privacidad/',         views.privacidad,         name='privacidad'),

    # ── Dashboards ───────────────────────────────────────────────
    path('dashboard/admin/',     views.dashboard_admin,     name='dashboard_admin'),
    path('dashboard/colegio/',   views.dashboard_colegio,   name='dashboard_colegio'),
    path('dashboard/conductor/', views.dashboard_conductor, name='dashboard_conductor'),
    path('dashboard/monitora/',  views.dashboard_monitora,  name='dashboard_monitora'),
    path('dashboard/padre/',     views.dashboard_padre,     name='dashboard_padre'),

    # ── Perfil ───────────────────────────────────────────────────
    path('perfil/', views.perfil, name='perfil'),

    # ── Notificaciones ───────────────────────────────────────────
    path('notificaciones/',                          views.notificaciones,         name='notificaciones'),
    path('notificaciones/todas-leidas/',             views.marcar_todas_leidas,    name='marcar_todas_leidas'),
    path('notificaciones/<int:notif_id>/leida/',     views.marcar_leida,           name='marcar_leida'),
    path('notificaciones/<int:notif_id>/autorizar/', views.responder_autorizacion, name='responder_autorizacion'),
    path('notificaciones/<int:notif_id>/ausencia/',  views.responder_ausencia,     name='responder_ausencia'),

    # ── Monitora (acciones de recorrido) ─────────────────────────
    path('monitora/confirmar-lista/',               views.confirmar_lista,               name='confirmar_lista'),
    path('monitora/novedad-general/',               views.registrar_novedad_general,     name='registrar_novedad_general'),
    path('monitora/novedad/<str:documento>/',        views.registrar_novedad,             name='registrar_novedad'),
    path('monitora/datos-medicos/<str:documento>/', views.solicitar_autorizacion_medica, name='solicitar_autorizacion_medica'),

    # ── Reportes ─────────────────────────────────────────────────
    path('reportes/viajes/pdf/',   views.reporte_viajes_pdf,   name='reporte_viajes_pdf'),
    path('reportes/viajes/excel/', views.reporte_viajes_excel, name='reporte_viajes_excel'),
    path('reportes/viajes/',       views.reporte_viajes,       name='reporte_viajes'),
    path('reportes/pdf/',          views.reportes_pdf,         name='reportes_pdf'),
    path('reportes/excel/',        views.reportes_excel,       name='reportes_excel'),
    path('reportes/',              views.reportes,             name='reportes'),

    # ── Usuarios ─────────────────────────────────────────────────
    path('usuarios/',                       views.usuarios,          name='usuarios'),
    path('usuarios/nuevo/',                 views.usuarios_nuevo,    name='usuarios_nuevo'),
    path('usuarios/pdf/',                   views.usuarios_pdf,      name='usuarios_pdf'),
    path('usuarios/excel/',                 views.usuarios_excel,    name='usuarios_excel'),
    path('usuarios/<str:cedula>/editar/',   views.usuarios_editar,   name='usuarios_editar'),
    path('usuarios/<str:cedula>/eliminar/', views.usuarios_eliminar, name='usuarios_eliminar'),
    path('usuarios/<str:cedula>/reactivar/', views.usuarios_reactivar, name='usuarios_reactivar'),

    # ── Colegios ─────────────────────────────────────────────────
    path('colegios/',                     colegios_views.lista_colegios,   name='colegios'),
    path('colegios/nuevo/',               colegios_views.nuevo_colegio,    name='colegios_nuevo'),
    path('colegios/<str:nit>/editar/',    colegios_views.editar_colegio,   name='colegios_editar'),
    path('colegios/<str:nit>/eliminar/',  colegios_views.eliminar_colegio, name='colegios_eliminar'),

    # ── Estudiantes ──────────────────────────────────────────────
    path('estudiantes/',                          estudiantes_views.lista_estudiantes,   name='estudiantes'),
    path('estudiantes/nuevo/',                    estudiantes_views.nuevo_estudiante,    name='estudiante_nuevo'),
    path('estudiantes/pdf/',                      estudiantes_views.estudiantes_pdf,     name='estudiantes_pdf'),
    path('estudiantes/excel/',                    estudiantes_views.estudiantes_excel,   name='estudiantes_excel'),
    path('estudiantes/<str:documento>/editar/',   estudiantes_views.estudiante_editar,   name='estudiante_editar'),
    path('estudiantes/<str:documento>/eliminar/', estudiantes_views.estudiante_eliminar, name='estudiante_eliminar'),

    # ── Conductores ──────────────────────────────────────────────
    path('conductores/',                       conductores_views.lista_conductores, name='conductores'),
    path('conductores/nuevo/',                 conductores_views.conductor_nuevo,   name='conductor_nuevo'),
    path('conductores/<str:cedula>/editar/',   conductores_views.conductor_editar,  name='conductor_editar'),
    path('conductores/<str:cedula>/eliminar/', conductores_views.conductor_eliminar,name='conductor_eliminar'),

    # ── Conductor · acciones form (dashboard HTML) ───────────────
    path('conductor/iniciar/',   rutas_views.iniciar_recorrido_form,   name='iniciar_recorrido'),
    path('conductor/finalizar/', rutas_views.finalizar_recorrido_form, name='finalizar_recorrido'),
    path('conductor/llegada/',   rutas_views.notificar_llegada_form,   name='notificar_llegada'),

    # ── Conductor · API JSON (para clientes móviles / JS) ────────
    path('recorrido/iniciar/',   rutas_views.iniciar_recorrido,   name='api_iniciar_recorrido'),
    path('recorrido/llegada/',   rutas_views.notificar_llegada,   name='api_notificar_llegada'),
    path('recorrido/finalizar/', rutas_views.finalizar_recorrido, name='api_finalizar_recorrido'),

    # ── Monitoras ────────────────────────────────────────────────
    path('monitoras/',                         monitoras_views.lista_monitoras,  name='monitoras'),
    path('monitoras/nueva/',                   monitoras_views.monitora_nueva,   name='monitora_nueva'),
    path('monitoras/<str:cedula>/editar/',     monitoras_views.monitora_editar,  name='monitora_editar'),
    path('monitoras/<str:cedula>/eliminar/',   monitoras_views.monitora_eliminar,name='monitora_eliminar'),

    # ── Rutas ────────────────────────────────────────────────────
    path('rutas/lista/',       rutas_views.lista_rutas,      name='lista_rutas'),
    path('rutas/gestion/',     rutas_views.gestion_rutas,    name='rutas_gestion'),
    path('rutas/mapa/',        rutas_views.mapa_conductor,   name='mapa_conductor'),
    path('rutas/tiempo-real/', rutas_views.mapa_tiempo_real, name='mapa_tiempo_real'),
    path('rutas/monitoreo/',   rutas_views.monitoreo,        name='monitoreo'),
    path('rutas/',             rutas_views.lista_rutas,      name='rutas'),

    # ── Ubicación GPS ────────────────────────────────────────────
    path('ubicacion/actualizar/',         rutas_views.actualizar_ubicacion, name='actualizar_ubicacion'),
    path('ubicacion/<int:recorrido_id>/', rutas_views.obtener_ubicacion,    name='obtener_ubicacion'),

    # ── Pagos ─────────────────────────────────────────────────────
    path('pagos/crear/',         pagos_views.crear_pago,          name='crear_pago'),
    path('pagos/masivos/',       pagos_views.crear_pagos_masivos, name='crear_pagos_masivos'),
    path('pagos/procesar/',      pagos_views.procesar_pago,       name='pago_procesar'),
    path('pagos/pdf/',           pagos_views.pagos_pdf,           name='pagos_pdf'),
    path('pagos/excel/',         pagos_views.pagos_excel,         name='pagos_excel'),
    path('pagos/en-linea/',      pagos_views.pagos_en_linea,      name='pagos_en_linea'),

    # ── Pagos · Wompi ────────────────────────────────────────────
    path('pagos/wompi/datos/<str:codigo_pago>/', pagos_views.datos_widget_wompi,      name='datos_widget_wompi'),
    path('pagos/wompi/webhook/',                 pagos_views.webhook_wompi,           name='webhook_wompi'),
    path('pagos/wompi/confirmacion/',             pagos_views.confirmacion_pago_wompi, name='confirmacion_pago_wompi'),

    path('pagos/', pagos_views.lista_pagos, name='pagos'),

    # ── Novedades ────────────────────────────────────────────────
    path('conductor/novedad/',                   views.registrar_novedad_conductor, name='registrar_novedad_conductor'),
    path('novedades/',                           views.lista_novedades,             name='novedades'),
    path('novedades/<int:novedad_id>/resolver/', views.resolver_novedad,            name='resolver_novedad'),

    # ── Ausencias ────────────────────────────────────────────────
    path('padre/ausencia/', views.reportar_ausencia, name='reportar_ausencia'),

    # ── Admin · utilidades ───────────────────────────────────────
    path('admin/resetear-lista/', views.resetear_lista_recorrido, name='resetear_lista'),
]