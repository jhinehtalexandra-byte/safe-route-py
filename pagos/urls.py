from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_pagos, name='pagos'),
    path('en-linea/', views.pagos_en_linea, name='pagos_en_linea'),
    path('procesar/', views.procesar_pago, name='procesar_pago'),
    path('pdf/', views.pagos_pdf, name='pagos_pdf'),
    path('excel/', views.pagos_excel, name='pagos_excel'),

    # ── Wompi ──
    path('wompi/datos/<str:codigo_pago>/', views.datos_widget_wompi, name='datos_widget_wompi'),
    path('wompi/webhook/', views.webhook_wompi, name='webhook_wompi'),
    path('wompi/confirmacion/', views.confirmacion_pago_wompi, name='confirmacion_pago_wompi'),
]