# Generated by Django 2.0.1 on 2018-03-26 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0007_remove_activitycategory_opportunity_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='opportunities',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
