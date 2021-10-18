from .base import *

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
]

ADMINS = [('Tikhon', 'ticha56@mail.ru')]
HOST = 'https://mountainteaband.ru'
SECURE_SSL_HOST = 'https://mountainteaband.ru'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
