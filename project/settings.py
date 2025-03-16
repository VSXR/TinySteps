import os
import sys
from pathlib import Path
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _
from rest_framework.views import exception_handler

# ---------------------------------------------------------------
# CONFIGURACIONES BÁSICAS
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-elp3%(#9&c9-(5xco05=oh7)7b%zda3j@3qt8@$#dajqhj@^+b"

DEBUG = True  # TRUE: FOR LOCAL HOST ONLY (CSS, IMGs AND MEDIA WILL APPEAR CORRECTLY!)

# ---------------------------------------------------------------
# CONFIGURACIONES DE SEGURIDAD
# ---------------------------------------------------------------
ALLOWED_HOSTS = ['tinySteps-django.azurewebsites.net', '127.0.0.1', 'localhost']

CSRF_TRUSTED_ORIGINS = [
    'https://tinySteps-django.azurewebsites.net',  # URL de producción
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------------------------------
# APLICACIONES Y MIDDLEWARE
# ---------------------------------------------------------------
INSTALLED_APPS = [
    # Aplicaciones Django predeterminadas
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicaciones de terceros
    'crispy_forms',
    'crispy_bootstrap4',
    'rest_framework',
    'rest_framework.authtoken',
    'whitenoise.runserver_nostatic',
    
    # Aplicaciones propias
    'tinySteps.apps.TinyStepsConfig',
    'api.apps.ApiConfig',
]

# Configuración de Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF Middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------------------------------------------
# CONFIGURACIÓN DE URLS Y TEMPLATES
# ---------------------------------------------------------------
ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# ---------------------------------------------------------------
# CONFIGURACIÓN DE BASES DE DATOS
# ---------------------------------------------------------------
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# CONFIGURACION PARA BASE DE DATOS EN LOCAL
if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # PERO SI SE HACE DEPLOY, SE ACTIVA LA CONFIGURACION PARA BASE DE DATOS EN AZURE
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'djangoDB-prod',
            'HOST': 'tinySteps-proy2-db.postgres.database.azure.com',
            'USER': 'djangoAdmin',
            'PASSWORD': 'jango123A',
            'PORT': '5432',
            'OPTIONS': {
                'sslmode': 'require',
                'sslrootcert': 'Microsoft RSA Root Certificate Authority 2017.crt',
            }
        }
    }

# ---------------------------------------------------------------
# CONFIGURACIÓN DE INTERNACIONALIZACIÓN
# ---------------------------------------------------------------
# https://docs.djangoproject.com/en/5.1/topics/i18n/
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# https://dev.to/doridoro/adding-translation-to-django-portfolio-project-4g42

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# ---------------------------------------------------------------
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS Y MEDIA
# ---------------------------------------------------------------
# Rutas para archivos estáticos
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'tinySteps', 'static'),
]

# Configuración de archivos de medios (separada de estáticos)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ---------------------------------------------------------------
# CONFIGURACIÓN DE AUTENTICACIÓN
# ---------------------------------------------------------------
# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ---------------------------------------------------------------
# CONFIGURACIÓN DE REST FRAMEWORK
# ---------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler'
}

# ---------------------------------------------------------------
# EXTERNAL APIS
# ---------------------------------------------------------------
EDAMAM_APP_ID = 'dd63e92c'
EDAMAM_APP_KEY = '58c1318bf68b536cd04b07be47f3693c'
NEWS_API_KEY = '2ea41d5b4b114a5c808b9108a90e0e2d'
CURRENTS_API_KEY = 'VxLJ2ZsRmjdMjVNKVNqMe0Amde-fHlNJSNYA_pfaLJ7GmjHN'

# ---------------------------------------------------------------
# CONFIGURACIÓN DE CORREO ELECTRÓNICO
# ---------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'c4relecloud@gmail.com'
EMAIL_HOST_PASSWORD = 'mnvp swyl hjgr pdyl'
DEFAULT_FROM_EMAIL = 'c4relecloud@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ---------------------------------------------------------------
# OTRAS CONFIGURACIONES
# ---------------------------------------------------------------
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
