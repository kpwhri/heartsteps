# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2019-08-06 01:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_requests', '0007_auto_20190624_1750'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('walking_suggestions', '0012_configuration_pooling'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoolingServiceConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('use_pooling', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PoolingServiceRequest',
            fields=[
                ('servicerequest_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='service_requests.ServiceRequest')),
            ],
            bases=('service_requests.servicerequest',),
        ),
    ]