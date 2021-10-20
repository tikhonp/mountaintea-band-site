from django.contrib import admin

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


@admin.register(models.Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('concert', 'description', 'price', 'is_active')


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'concert', 'is_done', 'amount_sum', 'date_created')


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('number', 'transaction', 'price', 'is_active')


@admin.register(models.ConcertImage)
class ConcertImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'concert', 'image',)
