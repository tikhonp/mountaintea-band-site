from django.core.management.base import BaseCommand
from django.core.mail import get_connection, EmailMultiAlternatives
import datetime
from concert.models import Transaction, Ticket
import pytz
from django.conf import settings
from django.template.loader import render_to_string


def send_mass_html_mail(datatuple, fail_silently=False, user=None,
                        password=None, connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)


class Command(BaseCommand):
    help = 'Sends a messages with tickets to people. Do not use in production!'

    def add_arguments(self, parser):
        parser.add_argument(
            '--emails',
            action='store_true',
            help='Print all list of emails',
        )

        parser.add_argument(
            '--nosend',
            action='store_true',
            help='Disable sending messages only generate',
        )

        parser.add_argument(
            '--sendtolist',
            action='store_true',
            help='Input emails into console and send its to this list',
        )

    def handle(self, *args, **options):
        check = datetime.datetime(
            2021, 2, 28, 20, 30)
        transactions = Transaction.objects.filter(
            date_created__lte=pytz.utc.localize(check), is_done=True,
        )

        if options['sendtolist']:
            transactions = []
            print("Input email, divide enter")

            while True:
                email = input()

                if email == "":
                    break

                transaction = Transaction.objects.filter(user__email=email)
                if len(transaction) == 0:
                    print("THERE IS NO SUCH MAIL AS {}".format(email))
                    return

                for t in transaction:
                    transactions.append(t)

        datatuple = []
        for transaction in transactions:
            context = {
                'transaction': transaction.pk,
                'transaction_hash': transaction.get_hash(),
                'host': settings.HOST,
                'subject': 'Билет на концерт {}'.format(
                    transaction.concert.title),
                'concert': transaction.concert,
                'tickets': Ticket.objects.filter(transaction=transaction),
                'user': transaction.user,
            }

            html = render_to_string('email/new_ticket.html', context)
            plaintext = render_to_string('email/new_ticket.txt', context)

            tuple_value = (
                'Билет на концерт {}'.format(transaction.concert.title),
                plaintext,
                html,
                'Горный Чай <noreply@mountainteaband.ru>',
                [transaction.user.email],
            )
            datatuple.append(tuple_value)

        print(len(datatuple))

        if options['emails']:
            for i in datatuple:
                print(i[4][0])

        if not options['nosend']:
            send_mass_html_mail(datatuple)
        else:
            print("Send denied")
