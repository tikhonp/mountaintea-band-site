from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from concert.models import Transaction, Ticket, Concert
from django.core import exceptions
from django.template.loader import render_to_string
from django.core.mail import send_mail


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


def test(request, transaction):
    t = Transaction.objects.get(pk=transaction)
    ticket = Ticket.objects.filter(transaction=t)
    user = t.user
    html = render_to_string('email/new_ticket.html', {
        'subject': 'Билет на концерт {}'.format(t.concert.title),
        'concert': t.concert,
        'tickets': ticket,
        'user': user
    })
    plaintext = render_to_string('email/new_ticket.txt', {
        'subject': 'Билет на концерт {}'.format(t.concert.title),
        'concert': t.concert,
        'tickets': ticket,
        'user': user
    })

    send_mail(
        'Билет на концерт {}'.format(t.concert.title),
        plaintext,
        'Горный Чай <noreply@mountainteaband.ru>',
        [user.email],
        # headers={'X-Mailgun-Track': 'yes'},
        html_message=html,
    )
    return HttpResponse("OK")
