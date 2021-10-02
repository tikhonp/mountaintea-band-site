import hashlib
import random
from io import BytesIO

import qrcode
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name="the related user")
    phone = PhoneNumberField("user's phone", blank=True, null=True, help_text='Контактный телефон', default=None)

    def __str__(self):
        return "{} {}".format(self.user.username, self.phone)


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
def create_user_profile(instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# noinspection PyUnusedLocal
@receiver(post_save, sender=User)
def save_user_profile(instance, **kwargs):
    instance.profile.save()


class Concert(models.Model):
    title = models.CharField("concert title", max_length=255)
    description = models.TextField("concert description")
    place = models.CharField("name and address of place", max_length=255)
    place_url = models.URLField("url to place page")
    date_time = models.DateTimeField("concert date")
    is_active = models.BooleanField("concert active", default=True)

    template = models.TextField("template to show concert page", default='<p>Добавьте страницу концерта</p>')

    def __str__(self):
        return "{} {}".format(self.title, "активен" if self.is_active else "Закончен")


class Price(models.Model):
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, verbose_name="the related concert")

    CURRENCY_CHOICES = [
        ('RUB', 'рубль'),
        ('EUR', 'евро'),
        ('USD', 'доллар'),
        ('GBP', 'британский фунт')
    ]
    price = models.FloatField("price of ticket")
    currency = models.CharField("price currency", max_length=3, choices=CURRENCY_CHOICES, default='RUB')
    description = models.CharField("price description", max_length=255)

    is_active = models.BooleanField("price active", default=True)
    max_count = models.IntegerField("price max tickets", default=None, blank=True)

    def __str__(self):
        return "{} цена - {}".format(self.concert.title, self.price)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="the related user")
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, verbose_name="the related concert")

    is_done = models.BooleanField(default=False)
    date_created = models.DateTimeField("date time created", auto_now_add=True)
    date_closed = models.DateTimeField("date close", default=None, null=True)
    amount_sum = models.FloatField("amount sum", default=None, null=True)

    def __str__(self):
        return "{} {} {}".format(
            self.concert.title, self.user.username,
            "Оплачено" if self.is_done else "Не оплачено")

    def get_hash(self):
        hash_str = '{}&{}&{}'.format(
            self.pk,
            self.amount_sum,
            self.user.pk,
        )
        sha1_hash = hashlib.sha1(hash_str.encode())
        return sha1_hash.hexdigest()


class Ticket(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, verbose_name="the related transaction")
    price = models.ForeignKey(Price, on_delete=models.CASCADE, verbose_name="the related price")

    number = models.CharField("ticket number", max_length=6, unique=True)

    is_active = models.BooleanField("is ticket valid", default=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            while True:
                self.number = str(random.randint(100000, 999999))
                t = Ticket.objects.filter(number=self.number)
                if len(t) == 0:
                    break

        if self.price.max_count:
            t = Ticket.objects.filter(
                price=self.price,
                transaction__is_done=True
            )
            if len(t) >= self.price.max_count:
                self.price.is_active = False
                self.price.save()

        return super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return "{} | {} | {}".format(
            self.number, self.transaction, self.price)

    def get_hash(self):
        hash_str = '{}&{}&{}'.format(
            self.transaction.pk,
            self.price,
            self.number
        )
        sha1_hash = hashlib.sha1(hash_str.encode())
        return sha1_hash.hexdigest()

    def get_qrcode(self):
        """get buffer io with qr code image for email"""

        qrcode_img = qrcode.make('{}/staff/submit/{}/{}/'.format(
            settings.HOST,
            self.number,
            self.get_hash(),
        ))
        canvas = Image.new('RGB', (500, 500), 'white')
        canvas.paste(qrcode_img)
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        return buffer.getvalue()
