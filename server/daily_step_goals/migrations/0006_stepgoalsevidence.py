# Generated by Django 3.1.7 on 2021-12-17 06:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('daily_step_goals', '0005_delete_activityday'),
    ]

    operations = [
        migrations.CreateModel(
            name='StepGoalsEvidence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startdate', models.DateField()),
                ('enddate', models.DateField()),
                ('prev_startdate', models.DateField()),
                ('prev_enddate', models.DateField()),
                ('median', models.PositiveSmallIntegerField(null=True)),
                ('evidence', models.JSONField(null=True)),
                ('freetext', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
