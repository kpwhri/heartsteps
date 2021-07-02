# Generated by Django 3.1.7 on 2021-07-02 02:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fitbit_clock_face', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClockFaceStepCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('steps', models.PositiveIntegerField()),
                ('time', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
