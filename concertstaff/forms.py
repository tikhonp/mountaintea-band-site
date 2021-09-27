from django import forms
from phonenumber_field.formfields import PhoneNumberField
from concert.models import Concert


class AddTicketForm(forms.Form):
    error_css_class = 'is-invalid'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = [(concert.pk, concert.title) for concert in Concert.objects.filter(is_active=True)]

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
