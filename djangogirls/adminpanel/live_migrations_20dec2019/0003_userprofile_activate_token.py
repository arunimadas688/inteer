# Generated by Django 2.0.1 on 2018-02-05 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0002_banner_banner_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='activate_token',
            field=models.TextField(null=True),
        ),
    ]
