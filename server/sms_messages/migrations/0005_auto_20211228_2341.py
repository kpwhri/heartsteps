# Generated by Django 3.1.7 on 2021-12-28 23:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('participants', '0025_auto_20210909_0131'),
        ('sms_messages', '0004_auto_20211224_0629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twilioaccountinfo',
            name='study',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='participants.study'),
        ),
    ]
