from django.core.management.base import BaseCommand

from concert.emails import generate_ticket_email, send_mail
from concert.models import Transaction


class Command(BaseCommand):
    help = 'Sends email message if user did not got it'

    def add_arguments(self, parser):
        parser.add_argument(
            '-tid',
            help='Transaction is where to send mail',
            type=int, required=True
        )

    def handle(self, *args, **options):
        if not options['tid']:
            print("usage : ./manage.py send_new_email -tid=<id:int>\nTransaction id required.")
            return

        try:
            transaction = Transaction.objects.get(id=options['tid'])
        except Transaction.DoesNotExist:
            print("Invalid transaction id. Does not exist.")
            return

        print(f"Sending to {transaction.user.first_name}, with email: \"{transaction.user.email}\"...")

        send_mail(**generate_ticket_email(transaction, headers=True))

        print("Sent successfully!")
