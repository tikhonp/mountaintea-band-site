from django.contrib.auth.models import User
from rest_framework import serializers

from concert.models import Concert, Price, Profile, Ticket, Transaction
from concertstaff.models import Issue


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
        fields = '__all__'


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

    def get_url(self, instance):
        return instance.get_absolute_url()

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('price', 'transaction', 'transaction__user', 'transaction__user__profile')
        return queryset

    class Meta:
        model = Ticket
        fields = "__all__"
        extra_kwargs = {'url': {'read_only': True}}
