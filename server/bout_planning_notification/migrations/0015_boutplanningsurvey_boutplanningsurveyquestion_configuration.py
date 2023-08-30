# Generated by Django 3.1.7 on 2021-12-14 05:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0009_question_published'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bout_planning_notification', '0014_auto_20210922_0026'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoutPlanningSurvey',
            fields=[
                ('survey_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='surveys.survey')),
            ],
            bases=('surveys.survey',),
        ),
        migrations.CreateModel(
            name='BoutPlanningSurveyQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='surveys.question')),
            ],
            bases=('surveys.question',),
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]