from django.urls import path
from . import views

urlpatterns = [
    path('',                        views.home,                name='home'),
    path('login/',                  views.login_view,          name='login'),
    path('logout/',                 views.logout_view,         name='logout'),
    path('registrarse/',            views.registrarse,         name='registrarse'),
    path('contacto/',               views.contacto,            name='contacto'),
    path('dashboard/admin/',        views.dashboard_admin,     name='dashboard_admin'),
    path('dashboard/conductor/',    views.dashboard_conductor, name='dashboard_conductor'),
    path('dashboard/padre/',        views.dashboard_padre,     name='dashboard_padre'),
    path('usuarios/',               views.usuarios,            name='usuarios'),
    path('usuarios/nuevo/',         views.usuarios_nuevo,      name='usuarios_nuevo'),
    path('perfil/',                 views.perfil,              name='perfil'),
    path('reportes/',               views.reportes,            name='reportes'),
]