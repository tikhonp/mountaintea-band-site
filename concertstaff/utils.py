from urllib.parse import urlparse

from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import resolve_url


class StaffMemberRequiredMixin(AccessMixin):
    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())

        path = self.request.build_absolute_uri()
        resolved_login_url = resolve_url(self.get_login_url())
        # If the login url is the same scheme and net location then use the
        # path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (
                (not login_scheme or login_scheme == current_scheme) and (not login_netloc or login_netloc == current_netloc)
        ):
            path = self.request.get_full_path()
        return redirect_to_login(
            path,
            resolved_login_url,
            self.get_redirect_field_name(),
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not (self.request.user.is_staff or self.request.user.is_superuser):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
