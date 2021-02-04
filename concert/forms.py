from django import forms
from phonenumber_field.formfields import PhoneNumberField


class BuyTicketForm(forms.Form):
    error_css_class = 'is-invalid'

    name = forms.CharField(
        max_length=150,
        label="Имя и Фамилия",
        required=True,
        widget=forms.TextInput()
    )
    email = forms.CharField(
        required=True,
        label="Электронная почта",
        widget=forms.EmailInput()
    )
    phone_number = PhoneNumberField(
        required=True,
        label="Номер телефона",
    )

    def __init__(self, *args, **kwargs):
        super(BuyTicketForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
