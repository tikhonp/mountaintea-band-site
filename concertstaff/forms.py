from django import forms
from phonenumber_field.formfields import PhoneNumberField

from concert.emails import generate_ticket_email, send_mail
from concert.models import Concert, Price, Transaction, Ticket
from concert.utils import create_user_payment
from django.utils import timezone


class AddTicketForm(forms.Form):
    error_css_class = 'is-invalid'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [(concert.pk, concert.title) for concert in Concert.objects.all() if concert.is_active]

        self.fields['concert'] = forms.ChoiceField(
            label='Концерт',
            required=True,
            choices=choices,
        )

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    concert = forms.ChoiceField(
        label='Концерт',
        required=True,
        choices=[],
    )

    name = forms.CharField(
        max_length=150,
        label='Имя и Фамилия',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Иван'})
    )
    email = forms.CharField(
        required=True,
        label='Электронная почта',
        widget=forms.EmailInput(attrs={'placeholder': 'mail2@mail.ru'}),
    )
    phone_number = PhoneNumberField(
        required=True,
        label='Номер телефона',
        widget=forms.TextInput(attrs={'placeholder': '+79123456789'})
    )

    def send_email(self, request):
        user = create_user_payment(self.cleaned_data)
        concert = Concert.objects.get(pk=self.cleaned_data.get('concert'))

        try:
            price = Price.objects.get(price=0., concert=concert)
        except Price.DoesNotExist:
            return 0

        transaction = Transaction.objects.create(
            user=user, concert=concert,
            date_closed=timezone.now(), amount_sum=0., is_done=True)
        Ticket.objects.create(transaction=transaction, price=price)

        tickets = Ticket.objects.filter(transaction=transaction)
        send_mail(**generate_ticket_email(transaction, tickets=tickets, request=request, headers=True))

        if not request.user.is_superuser:
            mail_managers(**generate_managers_ticket_email(transaction, tickets=tickets))
        return 1
