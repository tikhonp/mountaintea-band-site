import datetime
import hashlib

import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import mail_managers, send_mail
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import Template, RequestContext
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from concert import forms
from concert.models import Concert, Price, Transaction, Ticket


@require_http_methods(["GET"])
def main(request):
    return render(request, 'main.html', {
        'concerts': Concert.objects.filter(is_active=True)[:3]
    })


@require_http_methods(["GET"])
def concerts(request):
    return render(request, 'concerts.html', {
        'concerts': Concert.objects.filter(is_active=True)
    })


@require_http_methods(["GET"])
def concert_page(request, concert_id):
    base_t = """
    {% extends "base.html" %}

    {% load static %}

    {% block metrika %}{% include "metric.html" %}{% endblock %}

    {% block title %}{{ concert.title }}{% endblock %}
    """

    concert = get_object_or_404(Concert, pk=concert_id)
    template = Template(base_t + concert.template)
    context = RequestContext(request, {'concert': concert})

    return HttpResponse(template.render(context))


@require_http_methods(["GET", "POST"])
def buy_ticket(request, concert_id=None):
    if concert_id is None:
        return Http404('Please provide concert id')

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
            return HttpResponse("Ошибка sold out")

        form = forms.BuyTicketForm(request.POST)

        f_tickets = {}
        for price in prices:
            t = request.POST.get('pricecount{}'.format(price.id), '')
            if t == '' or int(t) == 0:
                continue
            f_tickets[price.id] = int(t)

        if f_tickets == {}:
            messages.error(request, "Вы должны добавить хотя бы один билет, чтобы совершить покупку")

        if form.is_valid() and f_tickets != {}:
            user, created = User.objects.get_or_create(
                username=form.cleaned_data.get('name').replace(' ', ''),
                first_name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email')
            )

            if not created:
                user.email = form.cleaned_data.get('email')

            user.profile.phone = form.cleaned_data.get('phone_number')
            user.save()

            request.session['user'] = user.id
            request.session['price'] = prices.first().id
            request.session['f_tickets'] = f_tickets

            transaction = Transaction.objects.create(user=user, concert=concert)

            for tick in f_tickets:
                for i in range(f_tickets[tick]):
                    ticket = Ticket.objects.create(
                        transaction=transaction,
                        price=Price.objects.get(id=tick)
                    )
                    amount_sum += ticket.price.price

            paying = True

    params = {
        'soldout': sold_out,
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
    hash_str = "{}&{}&{}&{}&{}&{}&{}&{}&{}".format(
        request.POST.get('notification_type', ''),
        request.POST.get('operation_id', ''),
        request.POST.get('amount', ''),
        request.POST.get('currency', ''),
        request.POST.get('datetime', ''),
        request.POST.get('sender', ''),
        request.POST.get('codepro', ''),
        settings.YANDEX_NOTIFICATION_SECRET,
        request.POST.get('label', ''),
    )
    hash_object = hashlib.sha1(hash_str.encode())

    if str(hash_object.hexdigest()) != request.POST.get('sha1_hash'):
        return HttpResponseBadRequest("Failed to check SHA1 hash")

    label = request.POST.get('label')
    if label is None:
        return HttpResponse("ok")
    if not label.isdigit():
        return HttpResponseBadRequest("Label is not valid digit")

    transaction = get_object_or_404(Transaction, id=int(label))

    transaction.date_closed = pytz.utc.localize(
        datetime.datetime.strptime(request.POST.get('datetime'), '%Y-%m-%dT%H:%M:%SZ')
    )
    transaction.amount_sum = float(request.POST.get('amount'))
    transaction.is_done = True
    transaction.save()
    tickets = Ticket.objects.filter(transaction=transaction)

    context = {
        'transaction': transaction.pk,
        'transaction_hash': transaction.get_hash(),
        'host': settings.HOST,
        'subject': 'Билет на концерт {}'.format(transaction.concert.title),
        'concert': transaction.concert,
        'tickets': tickets,
        'user': transaction.user,
    }

    html = render_to_string('email/new_ticket.html', context)
    plaintext = render_to_string('email/new_ticket.txt', context)

    send_mail(
        'Билет на концерт {}'.format(transaction.concert.title),
        plaintext,
        'Горный Чай <noreply@mountainteaband.ru>',
        [transaction.user.email],
        html_message=html,
        fail_silently=False,
    )

    mail_managers(
        'Куплен новый билет',
        '{}\n{}\n{}'.format(
            user.first_name,
            "\n".join(["{}\n{} р. (оплачено)\nНомер - {}\n---".format(
                i.price.description,
                i.price.price,
                i.number
            ) for i in tickets]),
            transaction.date_created),
        fail_silently=False
    )

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

    return render(request, 'email/new_ticket.html', {
        'html': True,
        'transaction': transaction.pk,
        'transaction_hash': transaction.get_hash(),
        'host': settings.HOST,
        'transaction_pk': transaction.pk,
        'concert': transaction.concert,
        'tickets': Ticket.objects.filter(transaction=transaction),
        'user': transaction.user
    })
