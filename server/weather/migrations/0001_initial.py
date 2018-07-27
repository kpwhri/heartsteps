# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherForecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('time', models.DateTimeField()),
                ('precip_probability', models.FloatField()),
                ('precip_type', models.CharField(max_length=32)),
                ('temperature', models.FloatField()),
                ('apparent_temperature', models.FloatField()),
                ('wind_speed', models.FloatField()),
                ('cloud_cover', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
