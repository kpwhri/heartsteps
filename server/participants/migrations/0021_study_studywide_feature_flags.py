# Generated by Django 3.1.7 on 2021-08-10 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0020_auto_20201129_0128'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='studywide_feature_flags',
            field=models.TextField(default=''),
        ),
    ]
