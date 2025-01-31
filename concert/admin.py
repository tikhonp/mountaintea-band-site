import csv
from io import StringIO

from django.contrib import admin
from django.http import HttpResponse

from concert import models


@admin.register(models.Concert)
class ConcertAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'start_date_time', 'place_name',)

    fieldsets = [
        (None, {'fields': [
            'title', 'description', 'performer', 'organizer', 'image']}),
        ('Date and status information', {'fields': [
            'start_date_time', 'end_date_time', 'status'
        ]}),
        ('Place information', {'fields': [
            'place_name', 'place_address', 'place_url', 'place_description',
        ]}),
        ('Templates', {'fields': [
            'page_template', 'email_template', 'email_title', 'promo_email_template', 'promo_email_title',
        ]}),
        ('Tickets and transactions', {'fields': [
            'max_tickets_count', 'buy_ticket_message', 'yandex_notification_secret', 'yandex_wallet_receiver',
        ]}),
    ]


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'accept_mailing', 'telegram_id')
    list_filter = ('accept_mailing', 'user__is_active')


@admin.register(models.Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('concert', 'description', 'price', 'is_active')
    list_filter = ('concert', 'is_active')


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    actions = ['download_csv']
    list_display = ('user', 'concert', 'is_done', 'amount_sum', 'date_created')
    list_filter = ('concert', 'is_done', 'date_created', 'email_status')

    def download_csv(self, request, queryset):
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "user", "user_first_name", "concert", "concert_title", "is_done", "date_created", "date_closed",
            "amount_sum", "email_status", "email_delivery_code", "email_delivery_message", "tickets_count"
        ])

        for s in queryset:
            writer.writerow([
                s.user.id, s.user.first_name, s.concert.id, s.concert.title, s.is_done, s.date_created, s.date_closed,
                s.amount_sum, s.email_status, s.email_delivery_code, s.email_delivery_message,
                models.Ticket.objects.filter(transaction=s).count()
            ])

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=transactions.csv'
        return response

    download_csv.short_description = "Download CSV file for selected transactions."


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('number', 'transaction', 'price', 'is_active')
    list_filter = ('price__concert', 'is_active')


@admin.register(models.ConcertImage)
class ConcertImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'concert', 'image',)
    list_filter = ('concert',)
