# Generated by Django 3.1.7 on 2021-12-14 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bout_planning_notification', '0015_boutplanningsurvey_boutplanningsurveyquestion_configuration'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoutPlanningMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
