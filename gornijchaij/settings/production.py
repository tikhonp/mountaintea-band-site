from .base import *
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://d0ff5c0a5a2941dabffa3896af63603e@o1075119.ingest.sentry.io/6075341",
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

DEBUG = False

ALLOWED_HOSTS = ['.mountainteaband.ru']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gornijchaij',
        'USER': 'gornijchaijuser',
        'PASSWORD': 'raspberry1',
        'HOST': 'localhost',
        'PORT': '',
    }
}

MANAGERS = [
    ('Tikhon', 'tikhon.petrishchev@gmail.com'),
    ('Platon', 'spektortosha@gmail.com'),
    ('Step', 'Stepaqwn@gmail.com'),
]

ADMINS = [('Tikhon', 'ticha56@mail.ru')]
HOST = 'https://mountainteaband.ru'
SECURE_SSL_HOST = 'https://mountainteaband.ru'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
