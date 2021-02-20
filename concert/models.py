from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField
import qrcode
from io import BytesIO
from PIL import Image
import random
from django.conf import settings
import hashlib


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    phone = PhoneNumberField(
        blank=True, help_text='Contact phone number', null=True, default=None)

    def __str__(self):
        return "{} {}".format(self.user.username, self.phone)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Concert(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(('Описание концерта'))
    place = models.CharField(max_length=255)
    place_url = models.URLField()
    date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} {}".format(
            self.title, "активен" if self.is_active else "Закончен")


class Price(models.Model):
    price = models.FloatField()
    description = models.CharField(max_length=255)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    max_count = models.IntegerField(default=None, null=True)

    def __str__(self):
        return "{} цена - {}".format(self.concert.title, self.price)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)
    date_created = models.DateTimeField(
        ('Время создания'), default=timezone.now)
    date_closed = models.DateTimeField(
        ('Время закрытия'), default=None, null=True)
    amount_sum = models.FloatField(
        ('Фактически пришло'), default=None, null=True)

    def __str__(self):
        return "{} {} {}".format(
            self.concert.title, self.user.username,
            "Оплачено" if self.is_done else "Не оплачено")


class Ticket(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    price = models.ForeignKey(Price, on_delete=models.CASCADE)
    number = models.CharField(max_length=6, unique=True)
    is_active = models.BooleanField(default=True)

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
                self.price.active = False
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
