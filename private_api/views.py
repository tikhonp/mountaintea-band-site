import json
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login
from rest_framework import filters
from rest_framework import viewsets, permissions, response, exceptions, generics, mixins
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action

from concert.models import Concert, Price, Transaction, Ticket
from concert.utils import create_user_payment
from concertstaff.models import Issue
from private_api.serializers import ConcertSerializer, PriceSerializer, UserSerializer, BuyTicketSerializer, \
    IssueSerializer, TicketSerializer, IncomingPaymentSerializer, MailgunEventPayloadSerializer, SmtpbzEventPayloadSerializer
from private_api.utils import CsrfExemptSessionAuthentication, ConcertIsDoneFilter


class ConcertViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Concert.objects.all()
    serializer_class = ConcertSerializer
    filter_backends = (ConcertIsDoneFilter,)
    filterset_fields = ['is_active']


class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['concert', 'is_active']


class CurrentUserViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        serializer = UserSerializer(request.user)
        return response.Response(serializer.data)


class BuyTicketApiView(generics.GenericAPIView):
    serializer_class = BuyTicketSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        concert = Concert.objects.get(id=serializer.data['concert_id'])
        prices = Price.objects.filter(concert=concert, is_active=True)

        if not prices:
            raise exceptions.APIException("Ошибка: билеты закончились.", code=410)

        if len([1 for t in serializer.data['tickets'] if isinstance(t['count'], int)]) == 0:
            raise exceptions.ValidationError("Введите корректное количество билетов.")

        user = create_user_payment(serializer.data['user'])
        login(request, user)

        transaction = Transaction.objects.create(user=user, concert=concert)

        for ticket in serializer.data['tickets']:
            for i in range(ticket['count']):
                Ticket.objects.create(transaction=transaction,
                                      price=Price.objects.get(id=ticket['id']))

        return response.Response({'transaction_id': transaction.id})


class IssueViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer


class IsStaffUser(permissions.BasePermission):
    """Allows access only to staff users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.all().select_related('transaction', 'transaction__concert', 'transaction__user', 'transaction__user__profile', 'price', 'price__concert')
    serializer_class = TicketSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ['transaction', 'is_active', 'price',
                        'transaction__is_done', 'transaction__concert']
    search_fields = ['transaction__user__first_name', 'transaction__user__email', 'transaction__user__username',
                     'number', 'price__description', 'price__price']
    permission_classes = (IsStaffUser | permissions.IsAdminUser,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    ordering_fields = ['transaction__date_created']

    @action(detail=True, methods=['put'], url_path='check/(?P<sha>[^/.]+)/(?P<concert_id>[^/.]+)')
    def check(self, request, pk=None, sha=None, concert_id=None):
        try:
            ticket = Ticket.objects.select_related(
                'transaction', 'transaction__user', 'price', 'transaction__concert').get(number=pk)
        except Ticket.DoesNotExist:
            raise exceptions.ValidationError("Билета номер \"{}\" не найдено.".format(pk))

        if sha != ticket.get_hash():
            raise exceptions.ValidationError(
                'Неверный sha hash валидации билета номер "{}".'.format(pk))

        valid = False
        if ticket.is_active and ticket.transaction.is_done and \
                ticket.transaction.concert.id == int(concert_id):
            ticket.is_active = False
            ticket.save()
            valid = True

        data = self.get_serializer(ticket).data
        data.update({"valid": valid, })

        return response.Response(data)


class IncomingPaymentView(generics.GenericAPIView):
    serializer_class = IncomingPaymentSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_email(request)
        return response.Response()


class SmtpbzWebhookView(generics.GenericAPIView):
    serializer_class = SmtpbzEventPayloadSerializer

    def post(self, request, event):
        print(request.data)
        tag = request.data.get('tag')
        if not tag:
            return response.Response()
        tid = json.loads(tag).get('tid')
        if not tid:
            return response.Response()
        transaction = get_object_or_404(Transaction, id=int(tid))
        message_status = request.data.get('message_status')
        transaction.email_status = event
        transaction.email_delivery_message = f"{message_status} {request.data.get('response')}"
        transaction.save()
        return response.Response()


class MailgunWebhookView(generics.GenericAPIView):
    serializer_class = MailgunEventPayloadSerializer

    def post(self, request, event):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validate_hmac()

        event_data = serializer.data.get('event-data')
        tid = event_data.get('user-variables', {}).get('tid')
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
        return response.Response()
