from django.contrib import admin

from concertstaff import models


@admin.register(models.Issue)
class ConcertImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_created', 'is_closed', 'manager')
