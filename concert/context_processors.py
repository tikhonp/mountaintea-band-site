from django.conf import settings


def template_settings(request):
    return {
        'host': settings.HOST,
        'debug': settings.DEBUG,
    }
