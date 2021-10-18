import json

import django
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


def find_profile(data: list, user_id: int) -> dict:
    for i in data:
        if i['model'] == 'concert.profile' and i['fields']['user'] == user_id:
            return i


def create_user(user_data: dict, data: list):
    print(user_data)
    user = User.objects.create(
        username=user_data['fields']['username'],
        first_name=user_data['fields']['first_name'],
        last_name=user_data['fields']['last_name'],
        email=user_data['fields']['email'],
    )
    user.profile.phone = find_profile(data, user_data['pk'])['fields']['phone']
    user.profile.save()


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
                if not i['fields']['is_superuser'] and not i['fields']['is_staff']:
                    try:
                        create_user(i, data)
                    except django.db.utils.IntegrityError:
                        print("ERROR")

        # create prices

        # for i in data:
        #     if i['model'] == 'concert.price':
        #         print(i)
        #         break
