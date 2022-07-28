from django.contrib.auth import login
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, permissions, response, exceptions, generics, mixins
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action

from concert.models import Concert, Price, Transaction, Ticket
from concert.utils import create_user_payment
from concertstaff.models import Issue
from private_api.serializers import ConcertSerializer, PriceSerializer, UserSerializer, BuyTicketSerializer, \
    IssueSerializer, TicketSerializer
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
                Ticket.objects.create(transaction=transaction, price=Price.objects.get(id=ticket['id']))

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
    queryset = Ticket.objects.all().order_by('-transaction__date_created')
    serializer_class = TicketSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_fields = ['transaction', 'is_active', 'price', 'transaction__is_done', 'transaction__concert']
    search_fields = ['transaction__user__first_name', 'transaction__user__email', 'transaction__user__username',
                     'number', 'price__description', 'price__price']
    permission_classes = (IsStaffUser | permissions.IsAdminUser,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @action(detail=True, methods=['put'], url_path='check/(?P<sha>[^/.]+)/(?P<concert_id>[^/.]+)')
    def check(self, request, pk=None, sha=None, concert_id=None):
        try:
            ticket = Ticket.objects.select_related(
                'transaction', 'transaction__user', 'price', 'transaction__concert').get(number=pk)
        except Ticket.DoesNotExist:
            raise exceptions.ValidationError("Билета номер \"{}\" не найдено.".format(pk))

        if sha != ticket.get_hash():
            raise exceptions.ValidationError('Неверный sha hash валидации билета номер "{}".'.format(pk))

        valid = False
        if ticket.is_active and ticket.transaction.is_done and \
                ticket.transaction.concert.id == int(concert_id):
            ticket.is_active = False
            ticket.save()
            valid = True

        data = self.get_serializer(ticket).data
        data.update({"valid": valid, })

        return response.Response(data)
