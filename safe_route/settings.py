from pathlib import Path
from decouple import config
import os
import dj_database_url

# ============================================
# RUTAS BASE
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SEGURIDAD
# ============================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [    'https://web-production-cadfa.up.railway.app',]

# ============================================
# APLICACIONES INSTALADAS
# ============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    # Apps del proyecto
    'usuarios',
    'rutas',
    'estudiantes',
    'pagos',
    'colegios',
    'conductores',
    'monitoras',
    'notificaciones',
]

# ============================================
# MIDDLEWARE — solo una vez, con WhiteNoise
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'safe_route.urls'

# ============================================
# TEMPLATES
# ============================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'safe_route.wsgi.application'

# ============================================
# BASE DE DATOS — PostgreSQL (local o Railway)
# ============================================
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql',
            'NAME':     config('DB_NAME'),
            'USER':     config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST':     config('DB_HOST'),
            'PORT':     config('DB_PORT'),
        }
    }

# ============================================
# VALIDACIÓN DE CONTRASEÑAS
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================
# IDIOMA Y ZONA HORARIA
# ============================================
LANGUAGE_CODE = 'es-co'
TIME_ZONE     = 'America/Bogota'
USE_I18N      = True
USE_TZ        = True

# ============================================
# ARCHIVOS ESTÁTICOS — WhiteNoise
# ============================================
STATIC_URL       = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT      = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================
# MEDIA — Cloudinary lo maneja
# ============================================
MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ============================================
# CLAVE PRIMARIA POR DEFECTO
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# EMAIL — Gmail SMTP
# ============================================
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_TIMEOUT       = 10
EMAIL_HOST_USER     = config('GMAIL_USER')
EMAIL_HOST_PASSWORD = config('GMAIL_APP_PASSWORD')
DEFAULT_FROM_EMAIL  = config('GMAIL_USER')

# ============================================
# WOMPI — Pasarela de pagos
# ============================================
WOMPI_PUBLIC_KEY       = config('WOMPI_PUBLIC_KEY')
WOMPI_PRIVATE_KEY      = config('WOMPI_PRIVATE_KEY')
WOMPI_INTEGRITY_SECRET = config('WOMPI_INTEGRITY_SECRET')
WOMPI_EVENTS_SECRET    = config('WOMPI_EVENTS_SECRET')
WOMPI_SANDBOX_URL      = config('WOMPI_SANDBOX_URL', default='https://sandbox.wompi.co/v1')

# ============================================
# CLOUDINARY — credenciales desde .env
# ============================================
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
    'API_KEY':    config('CLOUDINARY_API_KEY'),
    'API_SECRET': config('CLOUDINARY_API_SECRET'),
}