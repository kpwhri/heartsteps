# Generated by Django 3.1.7 on 2021-12-22 05:58

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bout_planning_notification', '0023_levelsequence_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='levelsequence_user',
            name='assigned',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
