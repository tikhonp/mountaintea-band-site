import logging

import django
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import Template, RequestContext
from django.views import View
from django.views.generic import ListView, TemplateView
from django.db.models import OuterRef, Exists

from concert.emails import generate_ticket_email, generate_concert_promo_email
from concert.models import Concert, Transaction, Ticket

logger = logging.getLogger(__name__)


class MainView(ListView):
    context_object_name = 'concerts'
    template_name = 'main.html'
    queryset = Concert.get_active_concerts_queryset()[:3]

    def post(self, request, *args, **kwargs):
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

        return self.get(request, *args, **kwargs)


class ConcertsView(ListView):
    context_object_name = 'concerts'
    model = Concert
    template_name = 'concerts.html'

    def get_queryset(self):
        return {
            'concerts_active': Concert.get_active_concerts_queryset().order_by('-start_date_time'),
            'concerts_disabled': Concert.objects.filter(~Exists(Concert.get_active_concerts_queryset().filter(pk=OuterRef('pk')))).order_by('-start_date_time')
        }


class ConcertPageView(View):
    queryset = Concert.objects.prefetch_related('concertimage_set', 'price_set')

    def get(self, request, concert_id):
        concert = get_object_or_404(self.queryset, pk=concert_id)
        template = Template(concert.page_template)

        return HttpResponse(
            template.render(RequestContext(request, {
                'concert': concert,
                'prices': concert.price_set.filter(is_active=True),
                **{'image_' + str(obj.id): obj for obj in concert.concertimage_set.all()},
            }))
        )


class BuyTicketView(TemplateView):
    template_name = 'buy_ticket.html'


class DonePaymentView(View):
    template_name = 'success_payment.html'

    def get(self, request):
        transaction_id = request.GET.get('t')
        if not transaction_id or not transaction_id.isdigit():
            return HttpResponseBadRequest("Invalid query params")

        user = get_object_or_404(Transaction.objects.select_related(
            'user'), pk=int(transaction_id)).user
        return render(request, self.template_name, {'user': user})


class QRCodeImageView(View):
    def get(self, request, ticket):
        ticket = get_object_or_404(Ticket, number=ticket)
        return HttpResponse(ticket.get_qrcode(), content_type="image/png")


class EmailPageView(View):
    def get(self, request, transaction, sha_hash):
        transaction = get_object_or_404(
            Transaction.objects.select_related('concert'), pk=transaction)

        if transaction.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid transaction hash")

        return HttpResponse(
            generate_ticket_email(transaction, request=request, is_web=True).get('html_message')
        )


class ConcertPromoEmailView(View):
    def get(self, request, concert_id, user, sha_hash):
        user = get_object_or_404(User.objects.select_related('profile'), pk=user)
        concert = get_object_or_404(Concert, pk=concert_id)

        if user.profile.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid user hash")

        return HttpResponse(
            generate_concert_promo_email(concert, user, request=request,
                                         is_web=True).get('html_message')
        )


class EmailUnsubscribeView(View):
    template_name = 'unsubscribe.html'

    def get(self, request, user, sha_hash):
        user = get_object_or_404(User.objects.select_related('profile'), pk=user)

        if user.profile.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid user hash")

        return render(request, self.template_name, {'user': user, 'get': request.method == 'GET'})

    def post(self, request, user, sha_hash):
        user = get_object_or_404(User.objects.select_related('profile'), pk=user)

        if user.profile.get_hash() != sha_hash:
            return HttpResponseBadRequest("Invalid user hash")

        if request.method == 'POST':
            user.profile.accept_mailing = False
            user.profile.save()

        return render(request, self.template_name, {'user': user, 'get': request.method == 'GET'})
