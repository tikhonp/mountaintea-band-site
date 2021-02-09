# Generated by Django 3.1.5 on 2021-02-07 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concert', '0003_auto_20210205_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='price',
            name='max_count',
            field=models.IntegerField(default=None, null=True),
        ),
    ]