# Generated by Django 2.0.2 on 2020-01-14 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0005_unlockpayementinformations'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplandetails',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
