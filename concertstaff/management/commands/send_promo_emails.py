from django.contrib.auth.models import User
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.management.base import BaseCommand

from concert.emails import generate_concert_promo_email
from concert.models import Transaction, Concert, Profile, ConcertImage


def send_mass_mail(data, fail_silently=False, connection=None):
    """Uses data (list of dicts with email data) to send mass mail"""

    connection = connection or get_connection(fail_silently=fail_silently)
    messages = []

    for m in data:
        message = EmailMultiAlternatives(
            m.get('subject'), m.get('message'), m.get('from_email'), m.get('recipient_list')
        )
        message.attach_alternative(m.get('html_message'), 'text/html')
        messages.append(message)

    return connection.send_messages(messages)


class Command(BaseCommand):
    help = 'Sends mass promo mails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--concert', type=int, help='concert id', required=True
        )

        parser.add_argument(
            '--emails',
            action='store_true',
            help='Print all list of emails',
        )

        parser.add_argument(
            '--no_send',
            action='store_true',
            help='Disable sending messages only generate',
        )

        parser.add_argument(
            '--send_to_list',
            action='store_true',
            help='Input emails into console and send its to this list',
        )

    def handle(self, *args, **options):
        concert = Concert.objects.get(pk=options.get('concert'))

        # generate recipient list
        recipient_list = []
        if options.get('send_to_list'):
            print("Input email, divide enter")

            email = input()
            while email != '':
                user = User.objects.filter(email=email)
                if user.count() == 0:
                    print("USER NOT FOUND!")
                    email = input()
                    continue

                recipient_list.append(user.first())

                email = input()
        else:
            done_transactions = Transaction.objects.filter(concert=concert, is_done=True)
            exclude_users_list = []
            for transaction in done_transactions:
                exclude_users_list.append(transaction.user.pk)

            for profile in Profile.objects.filter(accept_mailing=True):
                if profile.user.pk not in exclude_users_list and profile.user.email and profile.user.email != '':
                    recipient_list.append(profile.user)

        print("Total users: ", len(recipient_list))

        if options.get('emails'):
            for user in recipient_list:
                print(user.email)
            return

        # generate data

        data = []
        images = ConcertImage.objects.filter(concert=concert)
        for user in recipient_list:
            data.append(
                generate_concert_promo_email(concert, user, images=images)
            )

        if not options.get('no_send'):
            send_mass_mail(data)
        else:
            print("Send denied")
