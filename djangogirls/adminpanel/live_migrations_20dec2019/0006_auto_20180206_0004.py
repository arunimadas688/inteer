# Generated by Django 2.0.1 on 2018-02-06 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0005_auto_20180205_2355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cordinatorrequest',
            name='employee_number',
            field=models.TextField(blank=True, null=True),
        ),
    ]
