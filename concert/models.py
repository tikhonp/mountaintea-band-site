from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from phonenumber_field.modelfields import PhoneNumberField
import random


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

    def __str__(self):
        return "{} цена - {}".format(self.concert.title, self.price)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # price = models.ForeignKey(Price, on_delete=models.CASCADE)
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
    number = models.CharField(max_length=6)

    def save(self, *args, **kwargs):
        if not self.pk:
            while True:
                self.number = str(random.randint(100000, 999999))
                print("Generating new ticket number {}".format(self.number))
                t = Ticket.objects.filter(number=self.number)
                if len(t) == 0:
                    break

        return super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return "{} | {} | {}".format(
            self.number, self.transaction, self.price)
