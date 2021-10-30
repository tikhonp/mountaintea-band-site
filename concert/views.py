import datetime
import hashlib

import django
import pytz
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import mail_managers, send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import Template, RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from concert import forms
from concert.emails import generate_ticket_email, generate_managers_ticket_email, generate_concert_promo_email
from concert.models import Concert, Price, Transaction, Ticket, ConcertImage


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
        user, created = User.objects.get_or_create(
            username=cleaned_data.get('name').replace(' ', ''),
            first_name=cleaned_data.get('name'),
            email=cleaned_data.get('email')
        )
    except django.db.utils.IntegrityError:
        user, created = User.objects.get(username=cleaned_data.get('name').replace(' ', '')), False

    if not created:
        user.email = cleaned_data.get('email')

    user.profile.phone = cleaned_data.get('phone_number')
    user.save()
    return user


@require_http_methods(["GET", "POST"])
def buy_ticket(request, concert_id):
    concert = Concert.objects.get(id=concert_id)
    prices = Price.objects.filter(concert=concert, is_active=True)

    sold_out = False if prices else True

    paying = False
    transaction = None
    amount_sum = 0

    f_tickets = {}

    if request.method == 'GET':
        form = forms.BuyTicketForm()

        if not sold_out:
            user_id = request.session.get('user', False)
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    form = forms.BuyTicketForm({
                        'name': user.first_name,
                        'email': user.email,
                        'phone_number': user.profile.phone,
                    })
                except User.DoesNotExist:
                    request.session.pop('user', None)

            ft = request.session.get('f_tickets', False)
            if ft:
                ft = dict((int(name), val) for name, val in ft.items())
                f_tickets = ft

    else:
        if sold_out:
            return HttpResponse("Ошибка: билеты закончились.")

        form = forms.BuyTicketForm(request.POST)

        f_tickets = {}
        for price in prices:
            t = request.POST.get('price_count_{}'.format(price.id))
            if t and t.isdigit():
                if int(t) == 0:
                    continue
                else:
                    f_tickets[price.id] = int(t)

        if f_tickets == {}:
            messages.error(request, "Вы должны добавить хотя бы один билет, чтобы совершить покупку")

        elif form.is_valid():
            user = create_user_payment(form.cleaned_data)

            request.session['user'] = user.id
            request.session['price'] = prices.first().id
            request.session['f_tickets'] = f_tickets

            transaction = Transaction.objects.create(user=user, concert=concert)

            for tick in f_tickets:
                for i in range(f_tickets[tick]):
                    ticket = Ticket.objects.create(transaction=transaction, price=Price.objects.get(id=tick))
                    amount_sum += ticket.price.price

            paying = True

    params = {
        'sold_out': sold_out,
        'concert': concert,
        'price': prices.first(),
        'form': form,
        'paying': paying,
        'transaction': transaction,
        'prices': prices,
        'amount_sum': amount_sum,
        'f_tickets': f_tickets,
    }
    return render(request, 'buy_ticket.html', params)


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

    # print(str(hash_object.hexdigest()))

    if str(hash_object.hexdigest()) != request.POST.get('sha1_hash'):
        return HttpResponseBadRequest("Failed to check SHA1 hash")

    transaction.date_closed = pytz.utc.localize(
        datetime.datetime.strptime(request.POST.get('datetime'), '%Y-%m-%dT%H:%M:%SZ')
    )
    transaction.amount_sum = float(request.POST.get('amount'))
    transaction.is_done = True
    transaction.save()

    tickets = Ticket.objects.filter(transaction=transaction)
    send_mail(**generate_ticket_email(transaction, tickets=tickets, request=request))
    mail_managers(**generate_managers_ticket_email(transaction, tickets=tickets))

    return HttpResponse("ok")


def done_payment(request):
    transaction_id = request.GET.get('t')
    if not transaction_id or not transaction_id.isdigit():
        return HttpResponseBadRequest("Invalid query params")

    user = get_object_or_404(Transaction, pk=int(transaction_id))
    return render(request, 'success_payment.html', {'user': user})


@require_http_methods(["GET"])
def qr_code_image(request, ticket):
    ticket = get_object_or_404(Ticket, number=ticket)

    return HttpResponse(ticket.get_qrcode(), content_type="image/png")


@require_http_methods(["GET"])
def email_page(request, transaction, sha_hash):
    transaction = get_object_or_404(Transaction, pk=transaction)

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
