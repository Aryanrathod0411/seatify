import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


IS_VERCEL = os.environ.get('VERCEL') == '1'
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-development-key')
if IS_VERCEL and not os.environ.get('SECRET_KEY'):
    raise ImproperlyConfigured('Set SECRET_KEY in the Vercel project environment.')

DEBUG = os.environ.get('DEBUG', 'False' if IS_VERCEL else 'True').lower() in {
    'true', '1', 'yes'
}

VERCEL_HOSTS = [
    os.environ.get('VERCEL_URL'),
    os.environ.get('VERCEL_PROJECT_PRODUCTION_URL'),
]

ALLOWED_HOSTS = [
    'seatify-uzjf.onrender.com',
    'localhost',
    '127.0.0.1',
] + [host for host in VERCEL_HOSTS if host]
ALLOWED_HOSTS += [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]

CSRF_TRUSTED_ORIGINS = [
    f'https://{host}' for host in VERCEL_HOSTS if host
]
CSRF_TRUSTED_ORIGINS += [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]

if IS_VERCEL:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'accounts',
    'students',
    'rooms',
    'exams',
    'seating',
]

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

ROOT_URLCONF = 'seatify.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'seatify.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASE_URL = os.environ.get('DATABASE_URL')
if IS_VERCEL and not DATABASE_URL:
    raise ImproperlyConfigured(
        'Set DATABASE_URL to a persistent PostgreSQL database in Vercel.'
    )

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=0 if IS_VERCEL else 600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_ROOT = Path('/tmp/seatify-media') if IS_VERCEL else BASE_DIR / 'media'
MEDIA_URL = '/media/'


# Email
MAILERS = {
    'default': {
        'BACKEND': (
            'django.core.mail.backends.smtp.EmailBackend'
            if IS_VERCEL
            else 'django.core.mail.backends.console.EmailBackend'
        ),
        'OPTIONS': {
            'host': os.environ.get('EMAIL_HOST', 'localhost'),
            'port': int(os.environ.get('EMAIL_PORT', '25')),
            'username': os.environ.get('EMAIL_HOST_USER', ''),
            'password': os.environ.get('EMAIL_HOST_PASSWORD', ''),
            'use_tls': os.environ.get('EMAIL_USE_TLS', '').lower() in {
                'true', '1', 'yes'
            },
            'use_ssl': os.environ.get('EMAIL_USE_SSL', '').lower() in {
                'true', '1', 'yes'
            },
            'timeout': int(os.environ.get('EMAIL_TIMEOUT', '10')),
        },
    },
}
LOGIN_URL = '/faculty/login/'