# Generated by Django 3.1.7 on 2021-05-27 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nlm', '0005_auto_20210527_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='preloadedlevelsequencelevel',
            name='sequence_line',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='nlm.preloadedlevelsequenceline'),
            preserve_default=False,
        ),
    ]
