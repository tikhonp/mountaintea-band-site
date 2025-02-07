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

HOST = os.getenv("HOST")

ALLOWED_HOSTS = [
    os.getenv('DOMAIN'),
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
    # Setting this will send email on every new ticket
    # ('Tikhon', 'tikhon.petrishchev@gmail.com'),
]

ADMINS = [
    # Setting this will send prod errors to email
    # I use sentry for such case
    # ('Tikhon', 'tikhon.petrishchev@gmail.com'),
]

SECURE_SSL_HOST = HOST
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CORS_ALLOWED_ORIGINS = [
    HOST,
]


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
