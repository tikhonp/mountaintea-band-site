from django.conf import settings


def host(request):
    return {'host': settings.HOST}
