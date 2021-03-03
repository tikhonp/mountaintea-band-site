from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from concert.models import Transaction, Ticket, Concert, Price
from django.core import exceptions
from django.template.loader import render_to_string
from django.core.mail import send_mail, mail_managers, \
    get_connection, EmailMultiAlternatives
from django.conf import settings
from concertstaff import forms
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import redirect
import datetime
import pytz


@staff_member_required
def main(request):
    return render(request, 'main_staff.html', {
        'user': request.user,
        'concerts': Concert.objects.filter(is_active=True),
    })


@staff_member_required
@require_http_methods(["GET"])
def stat(request, concert):
    try:
        concert = Concert.objects.get(id=concert)
    except exceptions.ObjectDoesNotExist:
        return Http404("Conert does not exist")

    ticket = Ticket.objects.filter(
            transaction__is_done=True,
            transaction__concert=concert,
    ).order_by('-transaction__date_created')

    amount_sum = Transaction.objects.filter(
        is_done=True,
        concert=concert,
    ).aggregate(Sum('amount_sum'))['amount_sum__sum']

    return render(request, "stat.html", {
        "t": ticket,
        "amount_sum": amount_sum,
        "tickets_sum": len(ticket),
        "entered_persent": int(len(
            ticket.filter(is_active=False))*100/len(ticket))
    })


@staff_member_required
@require_http_methods(["GET", "POST"])
def ticket_check(request, ticket, sha):
    try:
        ticket = Ticket.objects.get(number=ticket)
    except exceptions.ObjectDoesNotExist:
        raise Http404('Ticket does not exists')

    if sha != ticket.get_hash():
        return HttpResponseBadRequest('Invalid sha hash')

    if request.method == 'GET':
        return render(request, 'submit_ticket.html', {
            'ticket': ticket,
        })

    else:
        ticket.is_active = False
        ticket.save()
        return HttpResponse("OK")


@staff_member_required
def test(request, transaction):
    transaction = Transaction.objects.get(pk=transaction)

    context = {
        'transaction': transaction.pk,
        'transaction_hash': transaction.get_hash(),
        'host': settings.HOST,
        'subject': 'Билет на концерт {}'.format(transaction.concert.title),
        'concert': transaction.concert,
        'tickets': Ticket.objects.filter(transaction=transaction),
        'user': transaction.user,
    }

    html = render_to_string('email/new_ticket.html', context)
    plaintext = render_to_string('email/new_ticket.txt', context)

    send_mail(
        'Билет на концерт {}'.format(transaction.concert.title),
        plaintext,
        'Горный Чай <noreply@mountainteaband.ru>',
        [transaction.user.email],
        # headers={'X-Mailgun-Track': 'yes'},
        html_message=html,
        fail_silently=False,
    )

    return HttpResponse("OK")


@staff_member_required
@require_http_methods(["GET", "POST"])
def add_ticket(request):
    created = False

    if request.method == 'GET':
        form = forms.AddTicketForm()
    else:
        form = forms.AddTicketForm(request.POST)

        if form.is_valid():
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

            concert = Concert.objects.get(pk=cd['concert'])

            price = Price.objects.filter(
                price=0.,
                concert=concert
            )
            if len(price) == 0:
                return HttpResponse("Необходимо создать Price с нулевой ценой, обратитесь к администратору")
            else:
                price = price.first()

            transaction = Transaction.objects.create(
                user=user,
                concert=concert,
                date_closed=timezone.now(),
                amount_sum=0.,
                is_done=True,
            )
            transaction.save()

            ticket = Ticket.objects.create(
                transaction = transaction,
                price = price,
            )
            ticket.save()

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

            send_mail(
                'Билет на концерт {}'.format(transaction.concert.title),
                plaintext,
                'Горный Чай <noreply@mountainteaband.ru>',
                [transaction.user.email],
                html_message=html,
                fail_silently=False,
            )

            if not request.user.is_superuser:
                mail_managers(
                    'Добавлен новый бесплатный билет',
                    '{}\n{}\n{}'.format(
                        transaction.user.first_name,
                        "\n".join(["{}\n{} р. (оплачено)\nНомер - {}\n---".format(
                            i.price.description,
                            i.price.price,
                            i.number
                        ) for i in Ticket.objects.filter(transaction=transaction)]),
                        transaction.date_created),
                    fail_silently=False
                )

            created = True
            form = forms.AddTicketForm()

    params = {
        'form': form,
        'created': created,
    }
    return render(request, 'free_ticket.html', params)


@staff_member_required
@require_http_methods(["GET", "POST"])
def submit_number(request):
    if request.method == 'GET':
        return render(request, 'submit_ticket_number.html')

    else:
        number = request.POST.get('ticket', '')
        try:
            ticket = Ticket.objects.get(number=number)
        except exceptions.ObjectDoesNotExist:
            return render(request, 'submit_ticket_number.html', {
                'number': number,
            })

        return redirect(
            '/staff/submit/{}/{}/'.format(number, ticket.get_hash()))
