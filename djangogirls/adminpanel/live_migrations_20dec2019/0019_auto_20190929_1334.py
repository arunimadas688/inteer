# Generated by Django 2.2.3 on 2019-09-29 13:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('adminpanel', '0018_auto_20180409_0652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opportunities',
            name='is_public',
        ),
        migrations.RemoveField(
            model_name='opportunities',
            name='is_recurring',
        ),
        migrations.RemoveField(
            model_name='opportunities',
            name='is_valid',
        ),
        migrations.RemoveField(
            model_name='reminders',
            name='status',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='status',
        ),
        migrations.CreateModel(
            name='OpportunityAnswers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.IntegerField(default=0, null=True)),
                ('answer', models.TextField(blank=True, null=True)),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.Opportunities')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]