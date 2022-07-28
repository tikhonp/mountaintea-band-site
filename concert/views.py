import datetime
import hashlib
import hmac
import json

import django
import pytz
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import mail_managers
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import Template, RequestContext
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from concert.emails import generate_ticket_email, generate_managers_ticket_email, generate_concert_promo_email, \
    send_mail
from concert.models import Concert, Price, Transaction, Ticket, ConcertImage

HOST = settings.HOST
MAILGUN_SIGNING_KEY = settings.MAILGUN_SIGNING_KEY


class MainView(ListView):
    context_object_name = 'concerts'
    queryset = Concert.get_main_queryset(3)
    template_name = 'main.html'

    def post(self, request):
        self.object_list = self.get_queryset()

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

        context = self.get_context_data()
        return self.render_to_response(context)


class ConcertsView(ListView):
    context_object_name = 'concerts'
    model = Concert
    template_name = 'concerts.html'

    def get_queryset(self):
        concerts_active, concerts_disabled = [], []
        for obj in Concert.objects.all():
            if obj.is_active:
                concerts_active.append(obj)
            else:
                concerts_disabled.append(obj)
        queryset = {'concerts_active': concerts_active,
                    'concerts_disabled': concerts_disabled}
        return queryset


class ConcertPageView(View):
    def get(self, request, concert_id):
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


class BuyTicketView(TemplateView):
    template_name = 'buy_ticket.html'


@method_decorator(csrf_exempt, name='dispatch')
class IncomingPaymentView(View):
    def post(self, request):
        label = request.POST.get('label')
        if label is None:
            return HttpResponse('ok')
        if not label.isdigit():
            return HttpResponseBadRequest('Label is not valid digit')

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

        if str(hash_object.hexdigest()) != request.POST.get('sha1_hash'):
            return HttpResponseBadRequest("Failed to check SHA1 hash")

        transaction.date_closed = pytz.utc.localize(
            datetime.datetime.strptime(request.POST.get('datetime'), '%Y-%m-%dT%H:%M:%SZ')
        )
        transaction.amount_sum = float(request.POST.get('amount'))
        transaction.is_done = True
        transaction.save()

        tickets = Ticket.objects.filter(transaction=transaction)
        send_mail(**generate_ticket_email(transaction, tickets=tickets, request=request, headers=True))
        mail_managers(**generate_managers_ticket_email(transaction, tickets=tickets))

        return HttpResponse("ok")


class DonePaymentView(View):
    template_name = 'success_payment.html'

    def get(self, request):
        transaction_id = request.GET.get('t')
        if not transaction_id or not transaction_id.isdigit():
            return HttpResponseBadRequest("Invalid query params")

        user = get_object_or_404(Transaction.objects.select_related('user'), pk=int(transaction_id)).user
        return render(request, self.template_name, {'user': user})


class QRCodeImageView(View):
    def get(self, request, ticket):
        ticket = get_object_or_404(Ticket, number=ticket)
        return HttpResponse(ticket.get_qrcode(), content_type="image/png")


class EmailPageView(View):
    def get(self, request, transaction, sha_hash):
        transaction = get_object_or_404(Transaction.objects.select_related('concert'), pk=transaction)

        if transaction.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid transaction hash")

        return HttpResponse(
            generate_ticket_email(transaction, request=request, is_web=True).get('html_message')
        )


class ConcertPromoEmailView(View):
    def get(self, request, concert_id, user, sha_hash):
        user = get_object_or_404(User, pk=user)
        concert = get_object_or_404(Concert, pk=concert_id)

        if user.profile.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid user hash")

        return HttpResponse(
            generate_concert_promo_email(concert, user, request=request, is_web=True).get('html_message')
        )


class EmailUnsubscribeView(View):
    template_name = 'unsubscribe.html'

    def get(self, request, user, sha_hash):
        user = get_object_or_404(User, pk=user)

        if user.profile.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid user hash")

        return render(request, self.template_name, {'user': user, 'get': request.method == 'GET'})

    def post(self, request, user, sha_hash):
        user = get_object_or_404(User, pk=user)

        if user.profile.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid user hash")

        if request.method == 'POST':
            user.profile.accept_mailing = False
            user.profile.save()

        return render(request, self.template_name, {'user': user, 'get': request.method == 'GET'})


@method_decorator(csrf_exempt, name='dispatch')
class MailgunWebhookView(View):
    def post(self, request, event):
        data = json.loads(request.body)

        signature = data.get('signature')
        hmac_digest = hmac.new(key=MAILGUN_SIGNING_KEY.encode(),
                               msg=('{}{}'.format(signature.get('timestamp'), signature.get('token'))).encode(),
                               digestmod=hashlib.sha256).hexdigest()
        if not hmac.compare_digest(str(signature.get('signature')), str(hmac_digest)):
            return HttpResponseBadRequest()

        event_data = data.get('event-data')
        tid = event_data.get('user-variables', {}).get('tid')
        if tid is None:
            return HttpResponse()

        transaction = get_object_or_404(Transaction, id=int(tid))

        event_status = event_data.get('event')
        if event_status is None:
            transaction.email_status = event
        else:
            transaction.email_status = event_status
            email_delivery_code = event_data.get('delivery-status', {}).get('code')
            if email_delivery_code:
                transaction.email_delivery_code = email_delivery_code
            email_delivery_message = event_data.get('delivery-status', {}).get('message')
            if email_delivery_message:
                transaction.email_delivery_message = email_delivery_message
        transaction.save()

        return HttpResponse()
