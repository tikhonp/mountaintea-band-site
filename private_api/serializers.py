from __future__ import annotations

import hashlib
import hmac
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import mail_managers
from django.shortcuts import get_object_or_404
from rest_framework import exceptions
from rest_framework import serializers

from concert.emails import generate_ticket_email
from concert.emails import send_mail, generate_managers_ticket_email
from concert.models import Concert, Price, Transaction, Ticket
from concert.models import Profile
from concertstaff.models import Issue

logger = logging.getLogger(__name__)


class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        exclude = ('page_template', 'email_template', 'yandex_notification_secret')


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, many=False)

    class Meta:
        model = User
        exclude = ['password', ]


class BuyTicketUserSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.CharField()
    phone_number = serializers.CharField()


class BuyTicketTicketSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    count = serializers.IntegerField()


class BuyTicketSerializer(serializers.Serializer):
    concert_id = serializers.IntegerField()
    user = BuyTicketUserSerializer(many=False)
    tickets = BuyTicketTicketSerializer(many=True)


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"


class TicketSerializer(serializers.ModelSerializer):
    price = PriceSerializer(read_only=True)
    transaction = TransactionSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    hash = serializers.SerializerMethodField()

    def get_url(self, instance):
        return instance.get_absolute_url()

    def get_hash(self, instance):
        return instance.get_hash()

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('price', 'transaction', 'transaction__user', 'transaction__user__profile')
        return queryset

    class Meta:
        model = Ticket
        fields = "__all__"
        extra_kwargs = {'url': {'read_only': True}}


class IncomingPaymentSerializer(serializers.Serializer):
    notification_type = serializers.CharField()
    operation_id = serializers.CharField()
    amount = serializers.FloatField()
    withdraw_amount = serializers.IntegerField(required=False)
    currency = serializers.CharField()
    datetime = serializers.DateTimeField()
    sender = serializers.CharField(allow_null=True)
    codepro = serializers.BooleanField()
    label = serializers.CharField()
    sha1_hash = serializers.CharField()
    unaccepted = serializers.BooleanField(required=False)

    def validate_sha(self, yandex_notification_secret: str):
        cleaned_data = self.context['request'].POST

        hash_str = "{notification_type}&{operation_id}&{amount}&{currency}&{datetime}&{sender}" \
                   "&{codepro}&{notification_secret}&{label}".format(
            notification_type=cleaned_data.get('notification_type'),
            operation_id=cleaned_data.get('operation_id'),
            amount=cleaned_data.get('amount'),
            currency=cleaned_data.get('currency'),
            datetime=cleaned_data.get('datetime'),
            sender=cleaned_data.get('sender'),
            codepro=cleaned_data.get('codepro'),
            notification_secret=yandex_notification_secret,
            label=cleaned_data.get('label'),
        )
        hash_object = hashlib.sha1(hash_str.encode())
        if str(hash_object.hexdigest()) != cleaned_data.get('sha1_hash'):
            if settings.DEBUG:
                logger.error("Failed to validate SHA1 hash, the hash is: {}".format(str(hash_object.hexdigest())))
            else:
                logger.error("Failed to validate SHA1 hash.")
            raise exceptions.ValidationError("Failed to check SHA1 hash.")

    def post_validate_label(self) -> int | None:
        label = self.data.get('label')
        if label == '':
            return None
        if not label.isdigit():
            raise exceptions.ValidationError("Label is not valid digit.")
        return int(label)

    def send_email(self, request) -> Transaction | None:
        label = self.post_validate_label()
        if not label:
            return None
        transaction = get_object_or_404(
            Transaction.objects.select_related('concert', 'user').prefetch_related('ticket_set'),
            id=label)
        self.validate_sha(transaction.concert.yandex_notification_secret)

        transaction.date_closed = self.data.get('datetime')
        transaction.amount_sum = self.data.get('amount')
        transaction.is_done = True
        transaction.save()

        send_mail(**generate_ticket_email(
            transaction, tickets=transaction.ticket_set.all(), request=request, headers=True))
        mail_managers(**generate_managers_ticket_email(transaction, tickets=transaction.ticket_set.all()))

        return transaction


class MailgunUserVariblesSerializer(serializers.Serializer):
    tid = serializers.IntegerField()


class MailgunDeliveryStatusSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    message = serializers.CharField(required=False)


class MailgunEventDataSerializer(serializers.Serializer):
    event = serializers.CharField(required=False)
    timestamp = serializers.CharField()
    id = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user-variables'] = MailgunUserVariblesSerializer(required=False)
        self.fields['delivery-status'] = MailgunDeliveryStatusSerializer(required=False)


class MailgunEventSignatureSerializer(serializers.Serializer):
    timestamp = serializers.CharField()
    token = serializers.CharField()
    signature = serializers.CharField()


class MailgunEventPayloadSerializer(serializers.Serializer):
    signature = MailgunEventSignatureSerializer()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event-data'] = MailgunEventDataSerializer()

    def validate_hmac(self):
        signature = self.data.get('signature')
        hmac_digest = hmac.new(key=settings.MAILGUN_SIGNING_KEY.encode(),
                               msg=('{}{}'.format(signature.get('timestamp'), signature.get('token'))).encode(),
                               digestmod=hashlib.sha256).hexdigest()
        if not hmac.compare_digest(str(signature.get('signature')), str(hmac_digest)):
            if settings.DEBUG:
                logger.error("Failed to check HMAC hash, the hash is {}".format(str(hmac_digest)))
            else:
                logger.error("Failed to check HMAC hash")
            raise exceptions.ValidationError("Failed to check HMAC hash.")
