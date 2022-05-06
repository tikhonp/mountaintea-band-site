from django.db import models
from django.contrib.auth.models import User


class Issue(models.Model):
    title = models.CharField("title", max_length=128)
    description = models.TextField("description")

    contact_telegram = models.CharField("contact telegram link", max_length=128, null=True)
    contact_email = models.CharField("contact email", max_length=128, null=True)

    date_created = models.DateTimeField("date time created", auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name="the related manager", null=True, default=None
    )

    def get_absolute_url(self):
        return f'/staff/issue/{self.pk}/'
