from django.shortcuts import render
from concert.models import Concert, Price, Transaction, Ticket
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from concert import forms
from django.contrib.auth.models import User
from django.core import exceptions
from django.views.decorators.csrf import csrf_exempt
import hashlib
import datetime
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.mail import mail_managers, EmailMultiAlternatives
import pytz
from django.conf import settings


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
    try:
        concert = Concert.objects.get(id=concert_id)
    except exceptions.ObjectDoesNotExist:
        response = HttpResponse("Invalid concert (does not exist)")
        response.status_code = 400
        return response

    return render(request, 'concert.html', {
        'concert': concert
    })


@require_http_methods(["GET", "POST"])
def buy_ticket(request, concert_id=None):
    if concert_id is None:
        return Http404('Please provide concert id')

    concert = Concert.objects.get(id=concert_id)
    prices = Price.objects.filter(
        concert=concert,
        active=True,
    )

    paying = False
    transaction = None
    amount_sum = 0

    f_tickets = {}

    if request.method == 'GET':
        form = forms.BuyTicketForm()

        u = request.session.get('user', False)
        if u:
            try:
                u = User.objects.get(id=u)
                p = u.profile

                form = forms.BuyTicketForm({
                    'name': u.first_name,
                    'email': u.email,
                    'phone_number': p.phone,
                })
            except exceptions.ObjectDoesNotExist:
                request.session.pop('user', None)

        ft = request.session.get('f_tickets', False)

        if ft:
            ft = dict((int(name), val) for name, val in ft.items())
            f_tickets = ft

    else:
        form = forms.BuyTicketForm(request.POST)

        f_tickets = {}
        for price in prices:
            t = request.POST.get('pricecount{}'.format(price.id), '')
            if t == '' or int(t) == 0:
                continue
            f_tickets[price.id] = int(t)

        if f_tickets == {}:
            messages.error(request,
                           "Вы должны добавить хотя бы один билет, чтобы совершить покупку")

        if form.is_valid() and f_tickets != {}:
            cd = form.cleaned_data
            user = User.objects.filter(
                username=cd['name'].replace(" ", ""))
            if len(user) == 0:
                user = User.objects.create(
                    username=cd['name'].replace(" ", ""),
                    first_name=cd['name'],
                    email=cd['email']
                )
                p = user.profile
                p.phone = cd['phone_number']

                user.save()
                p.save()
            else:
                user = user.first()
                user.email = cd['email']
                user.profile.phone = cd['phone_number']
                user.save()

            request.session['user'] = user.id
            request.session['price'] = prices.first().id
            request.session['f_tickets'] = f_tickets

            transaction = Transaction.objects.create(
                user=user,
                concert=concert
            )
            transaction.save()
            for tick in f_tickets:
                for i in range(f_tickets[tick]):
                    ticket = Ticket.objects.create(
                        transaction=transaction,
                        price=Price.objects.get(id=tick)
                    )
                    ticket.save()
                    amount_sum += ticket.price.price

            paying = True

    params = {
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

    if settings.DEBUG:
        print(str(hash_object.hexdigest()))

    if str(hash_object.hexdigest()) != request.POST.get('sha1_hash', ''):
        return HttpResponseBadRequest("Failed to check SHA1 hash")

    label = request.POST.get('label', '')

    try:
        transaction = Transaction.objects.get(id=int(label))
    except exceptions.ObjectDoesNotExist:
        return HttpResponseBadRequest("Aborted object doesnt exist")

    date_closed = datetime.datetime.strptime(
        request.POST.get('datetime', ''), '%Y-%m-%dT%H:%M:%SZ')
    transaction.date_closed = pytz.utc.localize(date_closed)
    transaction.amount_sum = float(request.POST['amount'])
    transaction.is_done = True
    transaction.save()

    tickets = Ticket.objects.filter(transaction=transaction)

    u = transaction.user

    msg = render_to_string("tickets_email.html", {
        'concert': transaction.concert,
        'tickets': tickets,
        'u': u,
    })

    msg_plain = '''
            {},
            Поздравляем, {}! Вы теперь сможете попасть на этот концерт
            ---
            {}
            Обратите внимание, что на мероприятие допускаются старше 14 лет. Необходимо наличие документа удостоверяющего личность.
        '''.format(
        transaction.concert.title,
        u.first_name,
        "\n".join(["{}\n{} р. (оплачено)\nНомер - {}\n---".format(
                i.price.description,
                i.price.price,
                i.number
        ) for i in tickets])
    )

    email = EmailMultiAlternatives(
        'Билет на концерт {}'.format(transaction.concert.title),
        msg_plain,
        'Gornij Chaij Ltd. <noreply@mountainteaband.ru>',
        [u.email],
        headers={'X-Mailgun-Track': 'yes'},
    )
    email.attach_alternative(msg, "text/html")
    email.send()


    mail_managers(
        'Куплен новый билет',
        '{}\n{}\n{}'.format(
            u.first_name,
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
    u = request.GET.get('t', False)

    if u:
        try:
            user = Transaction.objects.get(pk=int(u))
        except (exceptions.ObjectDoesNotExist, ValueError):
            response = HttpResponse("Invalid query params")
            response.status_code = 400
            return response
    else:
        return HttpResponseBadRequest("Invalid query params")

    return render(request, 'success_payment.html', {
        'user': user,
    })


@require_http_methods(["GET"])
def qr_codeimage(request, ticket):
    try:
        t = Ticket.objects.get(number=ticket)
    except exceptions.ObjectDoesNotExist:
        raise Http404('Ticket does not exists')

    image_data = t.get_qrcode()
    return HttpResponse(image_data, content_type="image/png")
