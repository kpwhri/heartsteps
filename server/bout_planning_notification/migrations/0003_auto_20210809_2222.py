# Generated by Django 3.1.7 on 2021-08-09 22:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bout_planning_notification', '0002_auto_20210809_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firstboutplanningtime',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]