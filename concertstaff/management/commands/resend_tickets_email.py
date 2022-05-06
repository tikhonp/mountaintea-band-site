from django.core.management.base import BaseCommand

from concert.emails import generate_ticket_email, send_mail
from concert.models import Transaction, Concert
from django.utils import timezone


class Command(BaseCommand):
    help = 'Sends email message with ticket if user did not got it'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        concert = Concert.objects.get(id=3)
        transactions = Transaction.objects.select_related('concert', 'user').filter(
            is_done=True, concert=concert, date_closed__lte=timezone.now()
        )
        for transaction in transactions:
            print(transaction.id, transaction.user.first_name, transaction.user.email, concert.title)

        # print(f"Sending to {transaction.user.first_name}, with email: \"{transaction.user.email}\"...")
        #
        # send_mail(**generate_ticket_email(transaction, headers=True))
        #
        # print("Sent successfully!")
