import re

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core import exceptions
from django.core.mail import send_mail, mail_managers
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.template import Template, RequestContext
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_http_methods

from concert.models import Transaction, Ticket, Concert, Price, ConcertImage
from concert.views import create_user_payment
from concertstaff import forms


@staff_member_required
def main(request):
    return render(request, 'main_staff.html', {
        'user': request.user,
        'concerts': [obj for obj in Concert.objects.all() if obj.is_active],
    })


@staff_member_required
@require_http_methods(["GET"])
def stat(request, concert):
    concert = get_object_or_404(Concert, id=concert)

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
        "entered_percent": entered_percent
    })


@staff_member_required
@require_http_methods(['GET', 'POST'])
def ticket_check(request, ticket, sha):
    ticket = get_object_or_404(Ticket, number=ticket)

    if sha != ticket.get_hash():
        return HttpResponseBadRequest('Invalid sha hash')

    if request.method == 'POST':
        ticket.is_active = False
        ticket.save()

    return render(request, 'submit_ticket.html', {'ticket': ticket})


@staff_member_required
@require_http_methods(['GET', 'POST'])
def add_ticket(request):
    created = False
    form = forms.AddTicketForm()

    if request.method == 'POST':
        form = forms.AddTicketForm(request.POST)

        if form.is_valid():
            user = create_user_payment(form.cleaned_data)

            concert = Concert.objects.get(pk=form.cleaned_data.get('concert'))

            try:
                price = Price.objects.get(price=0., concert=concert)
            except Price.DoesNotExist:
                return HttpResponse("Необходимо создать Price с нулевой ценой, обратитесь к администратору.")

            transaction = Transaction.objects.create(user=user, concert=concert, date_closed=timezone.now(),
                                                     amount_sum=0., is_done=True)
            Ticket.objects.create(transaction=transaction, price=price)

            images = ConcertImage.objects.filter(concert=transaction.concert)
            context = {
                'transaction': transaction.pk,
                'transaction_hash': transaction.get_hash(),
                'host': settings.HOST,
                'subject': transaction.concert.email_title,
                'concert': transaction.concert,
                'tickets': Ticket.objects.filter(transaction=transaction),
                'user': transaction.user,
                **{'image_' + str(obj.id): obj for obj in images}
            }

            html_email = Template(
                transaction.concert.email_template
            ).render(RequestContext(request, context))

            send_mail(
                transaction.concert.email_title,
                re.sub('[ \t]+', ' ', strip_tags(html_email)).replace('\n ', '\n').strip(),
                'Горный Чай <noreply@mountainteaband.ru>',
                [transaction.user.email],
                html_message=html_email,
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

    return render(request, 'free_ticket.html', {'form': form, 'created': created})


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
            return render(request, 'submit_ticket_number.html', {'number': number})

        return redirect('staff-ticket-check', ticket=number, sha=ticket.get_hash())
