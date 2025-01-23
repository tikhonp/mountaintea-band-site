# Generated by Django 3.2.16 on 2025-01-23 13:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, verbose_name='title')),
                ('description', models.TextField(verbose_name='description')),
                ('contact_telegram', models.CharField(max_length=128, null=True, verbose_name='contact telegram link')),
                ('contact_email', models.CharField(max_length=128, null=True, verbose_name='contact email')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='date time created')),
                ('is_closed', models.BooleanField(default=False)),
                ('manager', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='the related manager')),
            ],
        ),
    ]
