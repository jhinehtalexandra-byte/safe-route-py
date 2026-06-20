import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from usuarios import views

factory = RequestFactory()

# ── Helpers internos ───────────────────────────────────────

def test_sesion_activa_con_sesion():
    request = MagicMock()
    request.session.get.return_value = '111111'
    assert views._sesion_activa(request) == True

def test_sesion_activa_sin_sesion():
    request = MagicMock()
    request.session.get.return_value = None
    assert views._sesion_activa(request) == False

def test_es_admin_con_rol_admin():
    request = MagicMock()
    request.session.get.return_value = 'ADMIN'
    assert views._es_admin(request) == True

def test_es_admin_con_otro_rol():
    request = MagicMock()
    request.session.get.return_value = 'PADRE'
    assert views._es_admin(request) == False

def test_rol_en_admin_tiene_acceso_total():
    request = MagicMock()
    request.session.get.return_value = 'ADMIN'
    assert views._rol_en(request, 'CONDUCTOR') == True

def test_rol_en_rol_correcto():
    request = MagicMock()
    request.session.get.return_value = 'PADRE'
    assert views._rol_en(request, 'PADRE') == True

def test_rol_en_rol_incorrecto():
    request = MagicMock()
    request.session.get.return_value = 'PADRE'
    assert views._rol_en(request, 'ADMIN', 'CONDUCTOR') == False

# ── Modelo Usuario ─────────────────────────────────────────

@pytest.mark.django_db
def test_usuario_str(usuario_admin):
    assert 'Admin Test' in str(usuario_admin)
    assert 'ADMIN' in str(usuario_admin)

@pytest.mark.django_db
def test_usuario_es_admin(usuario_admin):
    assert usuario_admin.es_admin == True
    assert usuario_admin.es_padre == False

@pytest.mark.django_db
def test_usuario_activo_por_defecto(db):
    from usuarios.models import Usuario
    import bcrypt
    u = Usuario.objects.create(
        cedula='222222',
        tipo_documento='CEDULA_CIUDADANIA',
        user_name='user2',
        password=bcrypt.hashpw(b'Test1234!', bcrypt.gensalt()).decode(),
        nombre='Test User',
        email='test2@test.com',
        rol='PADRE',
    )
    assert u.activo == True