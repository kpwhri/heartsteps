# Generated by Django 3.1.7 on 2021-06-30 22:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nlm', '0012_auto_20210617_0313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='levelassignment',
            name='participant',
        ),
        migrations.RemoveField(
            model_name='levellineassignment',
            name='participant',
        ),
        migrations.AddField(
            model_name='levelassignment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='levellineassignment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
