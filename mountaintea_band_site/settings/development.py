from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '0.0.0.0',
    'localhost',
    'localhost:8000',
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

HOST = 'http://localhost:8000'

MANAGERS = [
    # ('Tikhon', 'tikhon.petrishchev@gmail.com'),
]

CORS_ALLOWED_ORIGINS = [
    'http://0.0.0.0:8000',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
