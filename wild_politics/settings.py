"""
Django settings for wild_politics project.

Generated by 'django-admin startproject' using Django 3.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not os.getenv('PROD')

ALLOWED_HOSTS = ['mysite.com', 'localhost', '127.0.0.1', '192.168.0.181', 'test.wildpolitics.online']

INTERNAL_IPS = ['127.0.0.1']

# Celery Configuration Options
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 950400
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_RESULT_EXPIRES = None
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 950400}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'django_celery_beat',
    'django_celery_results',

    'bootstrap3',
    'channels',

    'social_django',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    'allauth.socialaccount.providers.vk',
    'allauth.socialaccount.providers.google',

    'debug_toolbar',

    'article',
    'region',
    'party',
    'player',
    'state',
    'storage',
    'war',
    'chat',

    'django_cleanup',
    'fixture_magic',

]

SITE_ID = 1

SOCIAL_AUTH_URL_NAMESPACE = 'social'

if not os.getenv('HTTP_USE'):
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

sentry_environment = "production"
if not os.getenv('TOOL'):
    sentry_environment = "development"

if not sentry_environment == "development":
    sentry_sdk.init(
        environment=sentry_environment,
        dsn="https://91bebe2f57014429968500d11b987c5b@o877046.ingest.sentry.io/5827278",
        integrations=[DjangoIntegration()],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

USE_L10N = True
USE_THOUSAND_SEPARATOR = True
FORMAT_MODULE_PATH = [
    'wild_politics.formats',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_VK_OAUTH2_KEY = os.getenv('VK_KEY')
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.getenv('VK_PASS')

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


def show_toolbar(request):
    return not os.getenv('TOOL')


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

ROOT_URLCONF = 'wild_politics.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
            ],
        },
    },
]

WSGI_APPLICATION = 'wild_politics.wsgi.application'
ASGI_APPLICATION = "wild_politics.asgi.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wild_politics',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASS'),
        'HOST': 'db',
        'PORT': '5432',
        # 'ATOMIC_REQUESTS': 'True',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ru'

LANGUAGES = (
    ('ru', 'Russian'),
    ('en', 'English'),
    # ('fr', 'French'),
    # ('it', 'Italian'),
    # ('es', 'Spanish'),
    # ('pl', 'Polish'),
    # ('uk', 'Ukrainian'),
    # ('tr', 'Turkish'),
    # ('pt', 'Portuguese'),
)

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

# месторасположение файлов перевода
LOCALE_PATHS = (
    'locale',
    # os.path.join(PROJECT_DIR, 'locale'),
)

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# отладочная печать в Docker
level = 'DEBUG'
# level = 'WARNING'
if DEBUG:
    level = 'DEBUG'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': level,
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

class JResponse(JsonResponse):
    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, **kwargs):
        json_dumps_params = dict(ensure_ascii=False)
        super().__init__(data, encoder, safe, json_dumps_params, **kwargs)
