from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],

    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,

    send_default_pii=True
)

DEBUG = False

ALLOWED_HOSTS = [
    '0.0.0.0',
    '.mountainteaband.ru'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '',
    }
}

MANAGERS = [
    # ('Tikhon', 'tikhon.petrishchev@gmail.com'),
]

ADMINS = [
    ('Tikhon', 'tikhon.petrishchev@gmail.com'),
]

HOST = 'https://mountainteaband.ru'
SECURE_SSL_HOST = 'https://mountainteaband.ru'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CORS_ALLOWED_ORIGINS = [
    'https://mountainteaband.ru',
    'https://www.mountainteaband.ru',
]


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
