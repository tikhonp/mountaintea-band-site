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
    # ('Tikhon', 'ticha56@mail.ru'),
    # ('Миша', 'mmescherin@1553.ru'),
    # ('Степан', 'Stepaqw@mail.ru'),
    # ('Леша', 'leshich99@yandex.ru'),
]

ADMINS = [('Tikhon', 'ticha56@mail.ru')]
HOST = 'https://mountainteaband.ru'
SECURE_SSL_HOST = 'https://mountainteaband.ru'
