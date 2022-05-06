import datetime
import hashlib
import hmac
import json

import django
import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import mail_managers
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseGone
from django.shortcuts import render, get_object_or_404
from django.template import Template, RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from concert.emails import generate_ticket_email, generate_managers_ticket_email, generate_concert_promo_email, \
    send_mail
from concert.models import Concert, Price, Transaction, Ticket, ConcertImage
from concertstaff.models import Issue

HOST = settings.HOST
MAILGUN_SIGNING_KEY = settings.MAILGUN_SIGNING_KEY


@require_http_methods(["GET", "POST"])
def main(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            user.first_name = name
            user.save()
        except User.DoesNotExist:
            User.objects.create(
                username=name.replace(' ', ''),
                first_name=name,
                email=email
            )
        except django.contrib.auth.models.User.MultipleObjectsReturned:
            pass

    return render(request, 'main.html', {'concerts': [obj for obj in Concert.objects.all() if obj.is_active][:3]})


@require_http_methods(["GET"])
def concerts(request):
    concerts_active, concerts_disabled = [], []
    for obj in Concert.objects.all():
        if obj.is_active:
            concerts_active.append(obj)
        else:
            concerts_disabled.append(obj)
    return render(request, 'concerts.html', {
        'concerts_active': concerts_active, 'concerts_disabled': concerts_disabled
    })


@require_http_methods(["GET"])
def concert_page(request, concert_id):
    concert = get_object_or_404(Concert, pk=concert_id)
    template = Template(concert.page_template)
    images = ConcertImage.objects.filter(concert=concert)

    return HttpResponse(
        template.render(RequestContext(request, {
            'concert': concert,
            'prices': Price.objects.filter(concert=concert, is_active=True),
            **{'image_' + str(obj.id): obj for obj in images},
        }))
    )


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


@require_http_methods(["GET"])
def buy_ticket_data(request, concert_id):
    concert = get_object_or_404(Concert, id=concert_id)
    prices = Price.objects.filter(concert=concert, is_active=True)

    output = {
        'concert': {
            'title': concert.title,
            'date_time': timezone.localtime(concert.start_date_time).strftime("%d.%m в %H:%M"),
            'buy_ticket_message': concert.buy_ticket_message,
            'yandex_wallet_receiver': concert.yandex_wallet_receiver
        },
        'prices': [{
            'price': price.price,
            'description': price.description,
            'currency': price.currency,
            'id': price.id,
            'count': 0,
        } for price in prices],
        'user': None,
    }
    if request.user.is_authenticated:
        output['user'] = {
            'first_name': request.user.first_name,
            'email': request.user.email,
            'phone': str(request.user.profile.phone),
        }
    return HttpResponse(json.dumps(output))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def buy_ticket(request, concert_id):
    concert = Concert.objects.get(id=concert_id)
    prices = Price.objects.filter(concert=concert, is_active=True)

    if request.method == 'POST':
        if not prices:
            return HttpResponseGone(json.dumps({'error': 'Ошибка: билеты закончились.'}))

        data = json.loads(request.body)

        if len([1 for ticket_id, count in data.get('tickets').items() if isinstance(count, int)]) == 0:
            return HttpResponseBadRequest(json.dumps({
                'error': 'Введите корректное количество билетов.'
            }))

        user = create_user_payment(data.get('user'))
        login(request, user)

        transaction = Transaction.objects.create(user=user, concert=concert)

        for ticket_id, count in data.get('tickets').items():
            for i in range(int(count)):
                Ticket.objects.create(transaction=transaction, price=Price.objects.get(id=int(ticket_id)))

        return HttpResponse(json.dumps({'transaction_id': transaction.id}))

    return render(request, 'buy_ticket.html')


@csrf_exempt
@require_http_methods(["POST"])
def incoming_payment(request):
    label = request.POST.get('label')
    if label is None:
        return HttpResponse("ok")
    if not label.isdigit():
        return HttpResponseBadRequest("Label is not valid digit")

    transaction = get_object_or_404(Transaction, id=int(label))

    hash_str = "{}&{}&{}&{}&{}&{}&{}&{}&{}".format(
        request.POST.get('notification_type', ''),
        request.POST.get('operation_id', ''),
        request.POST.get('amount', ''),
        request.POST.get('currency', ''),
        request.POST.get('datetime', ''),
        request.POST.get('sender', ''),
        request.POST.get('codepro', ''),
        transaction.concert.yandex_notification_secret,
        request.POST.get('label', ''),
    )
    hash_object = hashlib.sha1(hash_str.encode())

    if str(hash_object.hexdigest()) != request.POST.get('sha1_hash'):
        return HttpResponseBadRequest("Failed to check SHA1 hash")

    transaction.date_closed = pytz.utc.localize(
        datetime.datetime.strptime(request.POST.get('datetime'), '%Y-%m-%dT%H:%M:%SZ')
    )
    transaction.amount_sum = float(request.POST.get('amount'))
    transaction.is_done = True
    transaction.save()

    tickets = Ticket.objects.filter(transaction=transaction)
    send_mail(**generate_ticket_email(transaction, tickets=tickets, request=request, headers=True))
    mail_managers(**generate_managers_ticket_email(transaction, tickets=tickets))

    return HttpResponse("ok")


def done_payment(request):
    transaction_id = request.GET.get('t')
    if not transaction_id or not transaction_id.isdigit():
        return HttpResponseBadRequest("Invalid query params")

    user = get_object_or_404(Transaction.objects.select_related('user'), pk=int(transaction_id)).user
    return render(request, 'success_payment.html', {'user': user})


@require_http_methods(["GET"])
def qr_code_image(request, ticket):
    ticket = get_object_or_404(Ticket, number=ticket)

    return HttpResponse(ticket.get_qrcode(), content_type="image/png")


@require_http_methods(["GET"])
def email_page(request, transaction, sha_hash):
    transaction = get_object_or_404(Transaction.objects.select_related('concert'), pk=transaction)

    if transaction.get_hash() != sha_hash:
        return HttpResponseBadRequest("Invalid transaction hash")

    return HttpResponse(
        generate_ticket_email(transaction, request=request, is_web=True).get('html_message')
    )


@require_http_methods(["GET"])
def concert_promo_email(request, concert_id, user, sha_hash):
    user = get_object_or_404(User, pk=user)
    concert = get_object_or_404(Concert, pk=concert_id)

    if user.profile.get_hash() != sha_hash:
        return HttpResponseBadRequest("Invalid user hash")

    return HttpResponse(
        generate_concert_promo_email(concert, user, request=request, is_web=True).get('html_message')
    )


@require_http_methods(["GET", "POST"])
def email_unsubscribe(request, user, sha_hash):
    user = get_object_or_404(User, pk=user)

    if user.profile.get_hash() != sha_hash:
        return HttpResponseBadRequest("Invalid user hash")

    if request.method == 'POST':
        user.profile.accept_mailing = False
        user.profile.save()

    return render(request, 'unsubscribe.html', {'user': user, 'get': request.method == 'GET'})


@csrf_exempt
@require_http_methods(["POST"])
def add_issue(request):
    data = json.loads(request.body)
    Issue.objects.create(**data)
    return HttpResponse()


@csrf_exempt
@require_http_methods(["POST"])
def mailgun_webhook(request, event):
    data = json.loads(request.body)

    signature = data.get('signature')
    hmac_digest = hmac.new(key=MAILGUN_SIGNING_KEY.encode(),
                           msg=('{}{}'.format(signature.get('timestamp'), signature.get('token'))).encode(),
                           digestmod=hashlib.sha256).hexdigest()
    if not hmac.compare_digest(str(signature.get('signature')), str(hmac_digest)):
        return HttpResponseBadRequest()

    event_data = data.get('event-data')
    tid = event_data.get('user-variables', {}).get('tid')
    if tid is None:
        return HttpResponse()

    transaction = get_object_or_404(Transaction, id=int(tid))

    event_status = event_data.get('event')
    if event_status is None:
        transaction.email_status = event
    else:
        transaction.email_status = event_status
        email_delivery_code = event_data.get('delivery-status', {}).get('code')
        if email_delivery_code:
            transaction.email_delivery_code = email_delivery_code
        email_delivery_message = event_data.get('delivery-status', {}).get('message')
        if email_delivery_message:
            transaction.email_delivery_message = email_delivery_message
    transaction.save()

    return HttpResponse()
