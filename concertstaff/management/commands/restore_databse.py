import json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from concert.models import Ticket, Price, Concert, Transaction


def create_user(old_user_id: dict, data: list) -> User:
    user_data = next(filter(lambda x: x['model'] == 'auth.user' and x['pk'] == old_user_id, data))['fields']
    try:
        return User.objects.get(
            username=user_data['username'],
        )
    except User.DoesNotExist:
        profile_data = next(filter(lambda x: x['model'] == 'concert.profile' and x['fields']['user'] == old_user_id, data))
        user = User.objects.create(
            password=user_data['password'],
            last_login=user_data['last_login'],
            username=user_data['username'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            is_active=user_data['is_active'],
            date_joined=user_data['date_joined'],
        )
        p = user.profile
        p.phone = profile_data['phone']
        p.save()
        print("Created user: ", user)
        return user


def creste_prices_for_first_concert(data) -> dict:
    prices_to_new_map = {}
    c = Concert.objects.get(pk=1)
    for price in filter(lambda x: x['model'] == 'concert.price', data):
        p = Price.objects.create(
            concert=c,
            price=price['fields']['price'],
            description=price['fields']['description'],
            is_active=False,
            max_count=price['fields']['max_count'],
        )
        prices_to_new_map[price["pk"]] = p.pk
        print(f'{price["pk"]}: {p.pk},')

    return prices_to_new_map


def create_transactions_and_tickets_for_first_concert(data, prices_to_new_map):
    c = Concert.objects.get(pk=1)
    for t in filter(lambda x: x['model'] == 'concert.transaction' and x['fields']['is_done'], data):
        user = create_user(t['fields']['user'], data)
        transaction = Transaction.objects.create(
            user=user,
            concert=c,
            is_done=t['fields']['is_done'],
            date_created=t['fields']['date_created'],
            date_closed=t['fields']['date_closed'],
            amount_sum=t['fields']['amount_sum'],
        )
        print("Created t: ", transaction)

        for ticket_data in filter(lambda x: x['model'] == 'concert.ticket' and x['fields']['transaction'] == t['pk'], data):
            ticket = Ticket.objects.create(
                transaction=transaction,
                price=Price.objects.get(pk=prices_to_new_map[ticket_data['fields']['price']]),
                number=ticket_data['fields']['number'],
                is_active=ticket_data['fields']['is_active'],
            )
            print("Created ticket: ", ticket)


class Command(BaseCommand):
    help = 'Sends email message if user did not got it'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json_data_file',
            help='file with json data',
            type=str, required=True
        )

    def handle(self, *args, **options):
        with open(options['json_data_file']) as f:
            data = json.load(f)

        create_transactions_and_tickets_for_first_concert(
            data,
            creste_prices_for_first_concert(data)
        )
