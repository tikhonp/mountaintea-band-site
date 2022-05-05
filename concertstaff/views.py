import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.postgres.search import SearchVector
from django.core import exceptions
from django.core.mail import send_mail, mail_managers
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from concert.emails import generate_ticket_email, generate_managers_ticket_email, send_mail
from concert.models import Transaction, Ticket, Concert, Price
from concert.views import create_user_payment
from concertstaff import forms
from concertstaff.models import Issue


@staff_member_required
def main(request):
    concerts = Concert.objects.all()
    return render(request, 'main_staff.html', {
        'user': request.user,
        'concerts': [obj for obj in concerts if obj.is_active],
        'concerts_done': [obj for obj in concerts if not obj.is_active],
        'working_issues': Issue.objects.filter(manager=request.user, is_closed=False),
        'available_issues': Issue.objects.filter(manager=None, is_closed=False),
    })


@staff_member_required
@require_http_methods(["GET"])
def stat(request, concert):
    get_object_or_404(Concert, id=concert)
    return render(request, "stat.html")


@staff_member_required
@require_http_methods(["GET"])
def stat_data(request, concert):
    concert = get_object_or_404(Concert, id=concert)
    query = request.GET.get('query', '')

    if query == '':
        tickets = Ticket.objects.select_related('price', 'transaction', 'transaction__user').filter(
            transaction__is_done=True,
            transaction__concert=concert,
        ).order_by('-transaction__date_created')
    else:
        tickets = Ticket.objects.select_related('price', 'transaction', 'transaction__user').filter(
            transaction__is_done=True,
            transaction__concert=concert,
        ).order_by('-transaction__date_created').annotate(
            search=SearchVector(
                'transaction__user__first_name', 'transaction__user__email',
                'transaction__user__username', 'number', 'price__description', 'price__price'
            ),
        ).filter(search=query)

    amount_sum = Transaction.objects.filter(
        is_done=True,
        concert=concert,
    ).aggregate(Sum('amount_sum'))['amount_sum__sum']

    tickets_sum = tickets.count()
    entered_percent = int(tickets.filter(is_active=False).count() * 100 / tickets_sum if tickets_sum != 0 else 0)

    return HttpResponse(json.dumps({
        "tickets": [{
            "number": ticket.number,
            "is_active": ticket.is_active,
            "get_hash": ticket.get_hash(),
            "price": {
                "id": ticket.price.id,
                "description": ticket.price.description,
                "price": ticket.price.price,
            },
            "transaction": {
                "date_created": timezone.localtime(
                    ticket.transaction.date_created).strftime("%H:%M %d.%m.%y"),
                "user": {
                    "first_name": ticket.transaction.user.first_name,
                    "pk": ticket.transaction.user.pk,
                },
                "email_status": ticket.transaction.email_status,
            }
        } for ticket in tickets],
        "amount_sum": amount_sum,
        "tickets_sum": tickets_sum,
        "entered_percent": entered_percent,
        "concert": {
            "title": concert.title,
        },
        "user": {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "is_superuser": request.user.is_superuser,
            "pk": request.user.pk,
        },
    }))


@staff_member_required
@require_http_methods(['GET', 'POST'])
def ticket_check(request, ticket, sha):
    ticket = get_object_or_404(Ticket, number=ticket)

    if sha != ticket.get_hash():
        return HttpResponseBadRequest('Invalid sha hash')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'use':
            ticket.is_active = False
            ticket.save()
        elif action == 'change_email':
            email = request.POST.get('email')
            send_email = request.POST.get('send_email')

            user = ticket.transaction.user
            user.email = email
            user.save()

            if send_email == 'on':
                send_mail(**generate_ticket_email(ticket.transaction, headers=True))
    return render(request, 'submit_ticket.html', {
        'ticket': ticket,
        'show_use_button': timezone.now().date() == ticket.transaction.concert.start_date_time.date()
    })


# @staff_member_required
@require_http_methods(['GET'])
def ticket_check_data(request, ticket, sha):
    try:
        ticket = Ticket.objects.get(number=ticket)
    except Ticket.DoesNotExist:
        return HttpResponse(json.dumps({
            'state': 'error',
            "error": "Билета номер \"{}\" не найдено.".format(ticket)
        }))

    if sha != ticket.get_hash():
        return HttpResponse(json.dumps({
            'state': 'error',
            'error': 'Неверный sha hash валидации билета номер "{}".'.format(ticket)
        }))

    valid = False
    if ticket.is_active and ticket.transaction.is_done:
        ticket.is_active = False
        ticket.save()
        valid = True

    return HttpResponse(json.dumps({
        'state': 'done',
        "number": ticket.number,
        "is_active": ticket.is_active,
        "valid": valid,
        "url": ticket.get_absolute_url(),
        "price": {
            "id": ticket.price.id,
            "description": ticket.price.description,
            "price": ticket.price.price,
        },
        "transaction": {
            "is_done": ticket.transaction.is_done,
            "date_created": timezone.localtime(
                ticket.transaction.date_created).strftime("%H:%M %d.%m.%y"),
            "user": {
                "first_name": ticket.transaction.user.first_name,
                "pk": ticket.transaction.user.pk,
            }
        }
    }))


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


@staff_member_required
@require_http_methods(["GET", "POST"])
def issue_page(request, issue):
    issue = get_object_or_404(Issue, id=issue)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'get_task':
            if issue.manager is None:
                issue.manager = request.user
                issue.save()
            else:
                return  # raise exception
        if action == 'done_task':
            if issue.manager == request.user:
                issue.is_closed = True
                issue.save()
            else:
                return  # raise exception

    is_manager = request.user == issue.manager

    return render(request, 'issue.html', {
        'issue': issue,
        'manager': 'вы' if is_manager else issue.manager,
        'is_manager': is_manager,
    })


@user_passes_test(lambda u: u.is_active and u.is_superuser, login_url='admin:login')
@require_http_methods(['GET'])
def qrcode(request):
    return render(request, 'qrcode.html')
