# Generated by Django 3.1.7 on 2022-03-03 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_api', '0052_fitbitaccountsummary'),
    ]

    operations = [
        migrations.CreateModel(
            name='FitbitConsumerKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=1000)),
                ('secret', models.CharField(max_length=1000)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]