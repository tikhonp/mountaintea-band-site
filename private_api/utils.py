from rest_framework import filters
from rest_framework.authentication import SessionAuthentication

from concert.models import Concert


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class ConcertIsDoneFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_active = request.query_params.get("is_active", None)
        if is_active and is_active.lower() == 'true':
            queryset = [concert for concert in Concert.objects.all() if concert.is_active]
        return queryset
