import html2text
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template import Template, Context, RequestContext

from concert.models import Transaction, Ticket, ConcertImage, Concert


def generate_ticket_email(
        transaction: Transaction, tickets=None, request: HttpRequest = None, is_web=False
) -> dict:
    """Render dict with email settings template with tickets based on the concert model settings"""

    tickets = tickets if tickets else Ticket.objects.filter(transaction=transaction)
    images = ConcertImage.objects.filter(concert=transaction.concert)

    context_dict = {
        'transaction': transaction.pk,
        'transaction_hash': transaction.get_hash(),
        'host': settings.HOST,
        'subject': transaction.concert.email_title,
        'concert': transaction.concert,
        'tickets': tickets,
        'user': transaction.user,
        'html': is_web,
        **{'image_' + str(obj.id): obj for obj in images}
    }
    context = RequestContext(request, context_dict) if request else Context(context_dict)
    html_email = Template(transaction.concert.email_template).render(context)
    plain_text = html2text.html2text(html_email)

    return {
        'subject': transaction.concert.email_title,
        'message': plain_text,
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'recipient_list': [transaction.user.email],
        'html_message': html_email,
    }


def generate_managers_ticket_email(transaction: Transaction, tickets: Ticket = None) -> dict:
    """Render text for managers email notified for new ticket"""

    tickets = tickets if tickets else Ticket.objects.filter(transaction=transaction)
    theme = f'Куплен новый билет на мероприятие {transaction.concert.full_title}!'

    tickets_text = ''
    for ticket in tickets:
        tickets_text += f"""
Билет номер "{ticket.number}":
{ticket.price.description} [{ticket.price.price} {ticket.price.currency}]
- - - - - - - - - - - - - - - - - - - - - - - - - - 
"""

    text = f"""
Пользователь {transaction.user.first_name} купил билетов: {tickets.count()}.
- - - - - - - - - - - - - - - - - - - - - - - - - - 
{tickets_text}

Дата и время: {transaction.date_created.strftime("%d/%m/%Y, %H:%M")}
    """

    return {
        'subject': theme,
        'message': text,
    }


def generate_concert_promo_email(
        concert: Concert, user: User, images=None, request: HttpRequest = None, is_web=False
) -> dict:
    """Render dict with settings for promo concert email"""

    images = images if images else ConcertImage.objects.filter(concert=concert)
    context_dict = {
        'user': user,
        'host': settings.HOST,
        'subject': concert.promo_email_title,
        'concert': concert,
        'html': is_web,
        **{'image_' + str(obj.id): obj for obj in images}
    }
    context = RequestContext(request, context_dict) if request else Context(context_dict)
    html_email = Template(concert.promo_email_template).render(context)
    plain_text = html2text.html2text(html_email)

    return {
        'subject': concert.promo_email_title,
        'message': plain_text,
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'recipient_list': [user.email],
        'html_message': html_email,
    }
