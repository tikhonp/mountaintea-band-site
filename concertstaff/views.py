from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core import exceptions
from django.core.mail import send_mail, mail_managers
from django.db.models import Sum
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from concert.models import Transaction, Ticket, Concert, Price
from concertstaff import forms


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

    entered_percent = int(len(ticket.filter(is_active=False)) * 100 / len(ticket)) if len(ticket) != 0 else 0

    return render(request, "stat.html", {
        "t": ticket,
        "amount_sum": amount_sum,
        "tickets_sum": len(ticket),
        "entered_persent": entered_percent
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
            user, created = User.objects.get_or_create(
                username=form.cleaned_data.get('name').replace(' ', ''),
                first_name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email')
            )

            if not created:
                user.email = form.cleaned_data.get('email')

            user.profile.phone = form.cleaned_data.get('phone_number')
            user.save()

            concert = Concert.objects.get(pk=form.cleaned_data.get('concert'))

            try:
                price = Price.objects.get(price=0., concert=concert)
            except Price.DoesNotExist:
                return HttpResponse("Необходимо создать Price с нулевой ценой, обратитесь к администратору")

            transaction = Transaction.objects.create(
                user=user,
                concert=concert,
                date_closed=timezone.now(),
                amount_sum=0.,
                is_done=True,
            )
            Ticket.objects.create(transaction=transaction, price=price)

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
