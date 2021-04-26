# Generated by Django 3.1.7 on 2021-04-26 18:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('participants', '0020_auto_20201129_0128'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CohortAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('cohort', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='participants.cohort')),
            ],
        ),
        migrations.CreateModel(
            name='StudyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('cohort_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nlm.cohortassignment')),
                ('participant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='participants.participant')),
                ('studytype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nlm.studytype')),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('studytype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nlm.studytype')),
            ],
        ),
        migrations.AddField(
            model_name='cohortassignment',
            name='studytype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nlm.studytype'),
        ),
        migrations.CreateModel(
            name='Conditionality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=1024)),
                ('module_path', models.CharField(max_length=1024, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('studytype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nlm.studytype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('name', 'user', 'studytype')},
            },
        ),
    ]