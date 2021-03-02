from django.core.management.base import BaseCommand
from concert.models import Transaction, Ticket
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core import exceptions


class Command(BaseCommand):
    help = 'Sends email message if user didn\'t got it'

    def add_arguments(self, parser):
        parser.add_argument(
            '-tid',
            help='REQUIRED: transaction is where to send mail',
            type=int,
        )

    def handle(self, *args, **options):
        if not options['tid']:
            print("usage : ./manage.py send_new_email -tid=<id:int>\nTransaction id required.")
            return

        try:
            transaction = Transaction.objects.get(id=options['tid'])
        except exceptions.ObjectDoesNotExist:
            print("Invalid transaction id. Does not exist.")
            return

        context = {
            'transaction': transaction.pk,
            'transaction_hash': transaction.get_hash(),
            'host': settings.HOST,
            'subject': 'Билет на концерт {}'.format(transaction.concert.title),
            'concert': transaction.concert,
            'tickets': Ticket.objects.filter(transaction=transaction),
            'user': transaction.user,
        }

        html = render_to_string('email/new_ticket.html', context)
        plaintext = render_to_string('email/new_ticket.txt', context)

        print("USER: {}\nEMAIL {}".format(
            context['user'].first_name,
            context['user'].email,
        ))

        send_mail(
            'Билет на концерт {}'.format(transaction.concert.title),
            plaintext,
            'Горный Чай <noreply@mountainteaband.ru>',
            [transaction.user.email],
            html_message=html,
            fail_silently=False,
        )

        print("Sent")
