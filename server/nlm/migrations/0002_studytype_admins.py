# Generated by Django 3.1.7 on 2021-04-26 19:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nlm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studytype',
            name='admins',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
