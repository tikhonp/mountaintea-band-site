from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    '10.0.1.106',
    'localhost',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

HOST = 'http://127.0.0.1:8000'

MANAGERS = [
    ('Tikhon', 'tikhon.petrishchev@gmail.com'),
]
