from django.contrib import admin

from concert import models

admin.site.register(models.Profile)
admin.site.register(models.Concert)
admin.site.register(models.Price)
admin.site.register(models.Transaction)
admin.site.register(models.Ticket)
admin.site.register(models.ConcertImage)
