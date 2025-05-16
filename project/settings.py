import os
import sys
import socket
import logging
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
import colorama

# Initialize
colorama.init()
load_dotenv()

# ---------------------------------------------------------------
# ENVIRONMENT CONFIGURATION
# ---------------------------------------------------------------
ENV = os.environ.get('DJANGO_ENV', 'development')  # Change to 'production' for production
if ENV not in ['development', 'production']:
    raise ValueError("DJANGO_ENV must be either 'development' or 'production'")
DEBUG = ENV == 'development' # This makes DEBUG=True by default. When set to 'production', DEBUG will be False!

# ---------------------------------------------------------------
# CORE SETTINGS
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY and not DEBUG:
    raise ValueError("SECRET_KEY environment variable is required in production")

ALLOWED_HOSTS = (
    ['*'] if DEBUG else os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
    .split(',')
)

# ---------------------------------------------------------------
# SECURITY SETTINGS
# ---------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://tinysteps-webapp-gwgkf2e6e4dqduh9.spaincentral-01.azurewebsites.net/',
    'https://tinysteps-6tb4.onrender.com',
    
]

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SECURE_SSL_REDIRECT = False

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------------------------------
# APPLICATIONS AND MIDDLEWARE
# ---------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap4',
    'rest_framework',
    'rest_framework.authtoken',
    'whitenoise.runserver_nostatic',
    'rosetta',
    'widget_tweaks',
]
PROJECT_APPS = [
    'tinySteps.apps.TinyStepsConfig',
    'api.apps.ApiConfig',
]

RUNNING_TESTS = 'test' in sys.argv

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS
if DEBUG and not RUNNING_TESTS:
    INSTALLED_APPS.insert(-len(PROJECT_APPS), 'debug_toolbar')

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tinySteps.utils.middleware.error_handling.ErrorHandler_Middleware',
]
if DEBUG and not RUNNING_TESTS:
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# ---------------------------------------------------------------
# URLS, TEMPLATES, WSGI
# ---------------------------------------------------------------
ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'custom_filters': 'tinySteps.custom_filters.custom_filters',
            },
        },
    },
]

# ---------------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------------
db_host = os.environ.get('DB_HOST')
can_connect_to_db = False

if db_host:
    try:
        socket.gethostbyname(db_host)
        can_connect_to_db = True
    except socket.gaierror:
        can_connect_to_db = False

if DEBUG or not can_connect_to_db:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Production database (PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': db_host,
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
                'sslrootcert': 'Microsoft RSA Root Certificate Authority 2017.crt',
            },
            'CONN_MAX_AGE': 60,  # Keep connections alive for 60 seconds
        }
    }

# ---------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# ---------------------------------------------------------------
# STATIC & MEDIA
# ---------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'tinySteps' / 'static']
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_MAX_AGE = 31536000

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------
# REST FRAMEWORK
# ---------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {'anon': '100/day', 'user': '1000/day'},
}

# ---------------------------------------------------------------
# EXTERNAL APIs & EMAIL
# ---------------------------------------------------------------
EDAMAM_APP_ID = os.environ.get('EDAMAM_APP_ID')
EDAMAM_APP_KEY = os.environ.get('EDAMAM_APP_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
CURRENTS_API_KEY = os.environ.get('CURRENTS_API_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ---------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': colorama.Fore.CYAN,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT,
        'RESET': colorama.Style.RESET_ALL,
    }
    def format(self, record):
        msg = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{msg}{self.COLORS['RESET']}"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {pathname}:{lineno} - {message}',
            'style': '{',
        },
        'standard': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
        'colored': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{levelname}] {message}',
            'style': '{',
        },
        'clean_console': {
            '()': ColoredFormatter,  # Use our custom formatter
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'exclude_autoreload': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'autoreload' not in record.name,
        },
        'exclude_static_finder': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'staticfiles.finders' not in record.name,
        },
        'exclude_migrations': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'migrations' not in record.name,
        },
        'exclude_template_debug': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'Exception while resolving variable' not in record.getMessage() 
                                      and 'template' not in record.name.lower(),
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true', 'exclude_autoreload', 'exclude_static_finder', 
                       'exclude_migrations', 'exclude_template_debug'],
            'class': 'logging.StreamHandler',
            'formatter': 'clean_console', 
        },
        'development': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'development.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'production': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'production.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'sql': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'sql.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Django's loggers
        'django': {
            'handlers': ['console', 'development', 'production'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'development'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'production', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'level': 'WARNING',
        },
        'django.template': {
            'handlers': ['development'],
            'level': 'WARNING',
            'propagate': False,
        },
        
        # Our application loggers
        'tinySteps': {
            'handlers': ['console', 'development', 'production'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'development', 'production'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Debug Toolbar logger
        'debug_toolbar': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------
# DEBUG TOOLBAR
# ---------------------------------------------------------------
if DEBUG and not RUNNING_TESTS:
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'ENABLE_STACKTRACES': True,
        'SHOW_COLLAPSED': True,
    }
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]

# ---------------------------------------------------------------
# MISCELLANEOUS SETTINGS
# ---------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
