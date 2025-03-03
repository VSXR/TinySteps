import os
import sys
from pathlib import Path
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-elp3%(#9&c9-(5xco05=oh7)7b%zda3j@3qt8@$#dajqhj@^+b"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # TRUE: FOR LOCAL HOST ONLY (CSS, IMGs AND MEDIA WILL APPEAR CORRECLTY!)!!

ALLOWED_HOSTS = ['tinySteps-django.azurewebsites.net', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'https://tinySteps-django.azurewebsites.net',  # URL de producción
]

# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'tinySteps.apps.TinyStepsConfig',
    'api.apps.ApiConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'whitenoise.runserver_nostatic',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # CSRF Middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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


# Database
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# URL para archivos estáticos y de medios
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Ruta para archivos de medios
MEDIA_ROOT = os.path.join(BASE_DIR, 'tinySteps', 'static', 'res', 'img', 'media')

# Ruta para archivos estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'tinySteps', 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'c4relecloud@gmail.com'
EMAIL_HOST_PASSWORD = 'mnvp swyl hjgr pdyl'
DEFAULT_FROM_EMAIL = 'c4relecloud@gmail.com'
