# Generated by Django 3.1.7 on 2021-03-06 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity_surveys', '0007_auto_20210306_0314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decision',
            name='activity_survey_id',
        ),
        migrations.AddField(
            model_name='decision',
            name='activity_survey',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='activity_surveys.activitysurvey'),
        ),
    ]
