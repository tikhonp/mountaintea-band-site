from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '0.0.0.0',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': '',
    }
}

HOST = 'http://0.0.0.0:8000'

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
