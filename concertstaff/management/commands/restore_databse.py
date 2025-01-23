import json

import django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


def find_profile(data: list, username: str) -> dict:
    for i in data:
        if i['model'] == 'concert.profile' and i['fields']['user'][0] == username:
            return i


def create_user(user_data: dict, data: list):
    print(user_data)
    user = User.objects.create(
        password=user_data['fields']['password'],
        last_login=user_data['fields']['last_login'],
        is_superuser=user_data['fields']['is_superuser'],
        username=user_data['fields']['username'],
        first_name=user_data['fields']['first_name'],
        last_name=user_data['fields']['last_name'],
        email=user_data['fields']['email'],
        is_staff=user_data['fields']['is_staff'],
        is_active=user_data['fields']['is_active'],
        date_joined=user_data['fields']['date_joined'],
    )
    p = user.profile
    profile_fields = find_profile(data, user_data['fields']['username'])['fields']
    p.phone = profile_fields['phone']
    p.accept_mailing = profile_fields['accept_mailing']
    p.telegram_id = profile_fields['telegram_id']
    p.save()


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

        # create users

        for i in data:
            if i['model'] == 'auth.user':
                # if not i['fields']['is_superuser'] and not i['fields']['is_staff']:
                try:
                    create_user(i, data)
                except django.db.utils.IntegrityError:
                    print("ERROR")

        # create prices

        # for i in data:
        #     if i['model'] == 'concert.price':
        #         print(i)
        #         break
