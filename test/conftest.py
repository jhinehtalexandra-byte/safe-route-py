import pytest
from django.test import Client
from usuarios.models import Usuario
import bcrypt

@pytest.fixture(scope='session')
def django_db_setup(django_test_environment, django_db_blocker):
    with django_db_blocker.unblock():
        from django.test.utils import setup_test_environment
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=0)

@pytest.fixture
def usuario_admin(db):
    return Usuario.objects.create(
        cedula         = "111111",
        tipo_documento = "CEDULA_CIUDADANIA",
        user_name      = "admin_test",
        password       = bcrypt.hashpw(b"Admin1234!", bcrypt.gensalt()).decode(),
        nombre         = "Admin Test",
        email          = "admin@test.com",
        rol            = "ADMIN",
        activo         = True,
    )

@pytest.fixture
def session_admin(client, usuario_admin):
    """Cliente con sesión de admin ya iniciada."""
    session = client.session
    session['usuario_cedula'] = usuario_admin.cedula
    session['usuario_nombre'] = usuario_admin.nombre
    session['usuario_rol']    = "ADMIN"
    session.save()
    return client