# Generated by Django 2.0.1 on 2018-03-23 01:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0006_auto_20180206_0004'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitycategory',
            name='opportunity_id',
        ),
    ]
