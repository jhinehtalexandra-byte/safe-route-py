import pytest
import bcrypt
from usuarios.models import Usuario

# ── Login ──────────────────────────────────────────────────

@pytest.mark.django_db
def test_login_exitoso(client, usuario_admin):
    response = client.post('/login/', {
        'username': 'admin_test',
        'password': 'Admin1234!'
    })
    assert response.status_code == 302  # redirige al dashboard

@pytest.mark.django_db
def test_login_password_incorrecta(client, usuario_admin):
    response = client.post('/login/', {
        'username': 'admin_test',
        'password': 'incorrecta'
    })
    assert response.status_code == 200  # vuelve al login con error
    assert 'error' in response.context

@pytest.mark.django_db
def test_login_usuario_inexistente(client):
    response = client.post('/login/', {
        'username': 'noexiste',
        'password': '123456'
    })
    assert response.status_code == 200
    assert 'error' in response.context

# ── CRUD Usuarios ──────────────────────────────────────────

@pytest.mark.django_db
def test_listar_usuarios(session_admin):
    response = session_admin.get('/usuarios/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_crear_usuario(session_admin):
    response = session_admin.post('/usuarios/nuevo/', {
        'cedula':         '999999',
        'tipo_documento': 'CEDULA_CIUDADANIA',
        'user_name':      'nuevo_user',
        'password':       'Pass1234!',
        'nombre':         'Usuario Nuevo',
        'email':          'nuevo@test.com',
        'rol':            'PADRE',
    })
    assert response.status_code == 302
    assert Usuario.objects.filter(cedula='999999').exists()

@pytest.mark.django_db
def test_editar_usuario(session_admin, usuario_admin):
    response = session_admin.post(f'/usuarios/{usuario_admin.cedula}/editar/', {
        'nombre':   'Nombre Editado',
        'email':    usuario_admin.email,
        'rol':      usuario_admin.rol,
        'activo':   'true',
    }, follow=True)
    assert response.status_code == 200

@pytest.mark.django_db
def test_eliminar_usuario(session_admin, usuario_admin):
    response = session_admin.get(
        f'/usuarios/{usuario_admin.cedula}/eliminar/',
        follow=True
    )
    assert response.status_code == 200
    usuario_admin.refresh_from_db()
    assert usuario_admin.activo == False

# ── Páginas públicas ───────────────────────────────────────

@pytest.mark.django_db
def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_terminos(client):
    response = client.get('/terminos/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_privacidad(client):
    response = client.get('/privacidad/')
    assert response.status_code == 200