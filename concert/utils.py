import django
from django.contrib.auth.models import User


def create_user_payment(cleaned_data: dict) -> User:
    try:
        user, created = User.objects.select_related('profile').get_or_create(
            username=cleaned_data.get('name').replace(' ', ''),
            first_name=cleaned_data.get('name'),
            email=cleaned_data.get('email')
        )
    except django.db.utils.IntegrityError:
        user, created = User.objects.select_related('profile').get(
            username=cleaned_data.get('name').replace(' ', '')), False

    if not created:
        user.email = cleaned_data.get('email')

    user.profile.phone = cleaned_data.get('phone_number')
    user.save()
    return user
