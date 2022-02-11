# Generated by Django 3.1.7 on 2022-02-10 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0007_auto_20190626_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyweatherforecast',
            name='category',
            field=models.CharField(choices=[('clear', 'Clear'), ('partially-cloudy', 'Partially Cloudy'), ('cloudy', 'Cloudy'), ('wind', 'Wind'), ('rain', 'Rain'), ('snow', 'Snow'), ('unknown', 'Unknown')], max_length=70),
        ),
    ]