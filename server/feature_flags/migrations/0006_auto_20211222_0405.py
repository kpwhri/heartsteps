# Generated by Django 3.1.7 on 2021-12-22 04:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feature_flags', '0005_featureflags_flags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featureflags',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
