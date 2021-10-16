import re

from django.conf import settings
from django.core import exceptions
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.template import Template, Context
from django.utils.html import strip_tags

from concert.models import Transaction, ConcertImage, Ticket


class Command(BaseCommand):
    help = 'Sends email message if user did not got it'

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

        images = ConcertImage.objects.filter(concert=transaction.concert)
        context = {
            'transaction': transaction.pk,
            'transaction_hash': transaction.get_hash(),
            'host': settings.HOST,
            'subject': 'Билет на концерт {}'.format(transaction.concert.title),
            'concert': transaction.concert,
            'tickets': Ticket.objects.filter(transaction=transaction),
            'user': transaction.user,
            **{'image_' + str(obj.id): obj for obj in images}
        }

        print("USER: {}\nEMAIL {}".format(context['user'].first_name, context['user'].email))

        html_email = Template(
            transaction.concert.email_template
        ).render(Context(context))

        send_mail(
            'Билет на концерт {}'.format(transaction.concert.title),
            re.sub('[ \t]+', ' ', strip_tags(html_email)).replace('\n ', '\n').strip(),
            'Горный Чай <noreply@mountainteaband.ru>',
            [transaction.user.email],
            html_message=html_email,
            fail_silently=False,
        )

        print("Sent")
