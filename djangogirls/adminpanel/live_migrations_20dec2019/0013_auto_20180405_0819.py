# Generated by Django 2.0.1 on 2018-04-05 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0012_auto_20180405_0818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='phone',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='phone2',
            field=models.TextField(blank=True, null=True),
        ),
    ]