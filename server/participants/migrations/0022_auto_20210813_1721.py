# Generated by Django 3.1.7 on 2021-08-13 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0021_study_studywide_feature_flags'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='study',
            options={'verbose_name': 'Study', 'verbose_name_plural': 'Studies'},
        ),
    ]
