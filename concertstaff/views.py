from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.postgres.search import SearchVector
from django.core import exceptions
from django.core.mail import send_mail, mail_managers
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from concert.emails import generate_ticket_email, generate_managers_ticket_email
from concert.models import Transaction, Ticket, Concert, Price
from concert.views import create_user_payment
from concertstaff import forms


@staff_member_required
def main(request):
    concerts = Concert.objects.all()
    return render(request, 'main_staff.html', {
        'user': request.user,
        'concerts': [obj for obj in concerts if obj.is_active],
        'concerts_done': [obj for obj in concerts if not obj.is_active]
    })


@staff_member_required
@require_http_methods(["GET", "POST"])
def stat(request, concert):
    concert = get_object_or_404(Concert, id=concert)

    tickets = Ticket.objects.filter(
        transaction__is_done=True,
        transaction__concert=concert,
    ).order_by('-transaction__date_created')

    amount_sum = Transaction.objects.filter(
        is_done=True,
        concert=concert,
    ).aggregate(Sum('amount_sum'))['amount_sum__sum']

    tickets_sum = tickets.count()
    entered_percent = int(tickets.filter(is_active=False).count() * 100 / tickets_sum if tickets_sum != 0 else 0)

    query = ''
    if request.method == 'POST':
        query = request.POST.get('query')
        tickets = tickets.annotate(
            search=SearchVector(
                'transaction__user__first_name', 'transaction__user__email',
                'transaction__user__username', 'number', 'price__description', 'price__price'
            ),
        ).filter(search=query)

    return render(request, "stat.html", {
        "t": tickets,
        "amount_sum": amount_sum,
        "tickets_sum": tickets_sum,
        "entered_percent": entered_percent,
        "concert": concert,
        "query": query,
        "user": request.user,
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

            tickets = Ticket.objects.filter(transaction=transaction)
            send_mail(**generate_ticket_email(transaction, tickets=tickets, request=request))

            if not request.user.is_superuser:
                mail_managers(**generate_managers_ticket_email(transaction, tickets=tickets))

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
