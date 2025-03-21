import os, socket
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

load_dotenv()

# ---------------------------------------------------------------
# CONFIGURACIONES BÁSICAS
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ---------------------------------------------------------------
# CONFIGURACIONES DE SEGURIDAD
# ---------------------------------------------------------------
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if not DEBUG else ['*']

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
    'tinySteps.middleware.broken_pipe_handler.BrokenPipeHandlerMiddleware',
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

db_host = os.environ.get('DB_HOST')
can_connect_to_db = False

if db_host:
    try:
        socket.gethostbyname(db_host)
        can_connect_to_db = True
    except socket.gaierror:
        can_connect_to_db = False

if DEBUG or not can_connect_to_db:
    # DEVELOPMENT DATABASE CONFIGURATION
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # PRODUCTION DATABASE CONFIGURATION
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': db_host,
            'PORT': os.environ.get('DB_PORT'),
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
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'tinySteps', 'static'),
]

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Static files storage configuration
if DEBUG:
    # Development configuration
    WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds (for caching static files)
else:
    # Production configuration
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
EDAMAM_APP_ID = os.environ.get('EDAMAM_APP_ID')
EDAMAM_APP_KEY = os.environ.get('EDAMAM_APP_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
CURRENTS_API_KEY = os.environ.get('CURRENTS_API_KEY')

# ---------------------------------------------------------------
# CONFIGURACIÓN DE CORREO ELECTRÓNICO
# ---------------------------------------------------------------
if DEBUG:
    # Development mode - print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production mode - send real emails
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = os.environ.get('EMAIL_PORT')
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# ---------------------------------------------------------------
# OTRAS CONFIGURACIONES
# ---------------------------------------------------------------
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------
# CONFIGURACIÓN DEL LOGGING
# ---------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'connection_errors.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'connection_errors': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}