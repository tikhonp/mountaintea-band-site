from django.core.management.base import BaseCommand

from concert.emails import generate_ticket_email, send_mail
from concert.models import Transaction, Concert
from django.utils import timezone
from datetime import datetime


class Command(BaseCommand):
    help = 'Sends email message with ticket if user did not got it'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        concert = Concert.objects.get(id=3)
        transactions = Transaction.objects.select_related('concert', 'user').filter(
            is_done=True, concert=concert, date_closed__lte=datetime(2022, 5, 6, 22, 31)
        )
        email = input()
        while email != '':
            for transaction in transactions:
                if transaction.user.email == email:
                    send_mail(**generate_ticket_email(transaction, headers=True))
                    print("ok")

            email = input()
